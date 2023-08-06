import time
import os
import paramiko
import uuid
import re

from celery import Task
from celery.utils.log import get_task_logger
from heatclient.exc import HTTPNotFound
from io import StringIO

from .utils import UP_STATES
from .heat import HeatWrapper
from .nova import NovaWrapper

logger = get_task_logger(__name__)


class LaunchStackTask(Task):
    """
    Launch, or if it already exists and is suspended, resume a stack for the
    user.

    """
    def run(self,
            configuration,
            stack_run,
            stack_name,
            stack_template,
            stack_user,
            reset=False):
        """
        Run the celery task.

        """
        status = ""
        verify_status = None
        error_msg = ""
        stack = None
        stack_ip = None
        stack_key = ""
        stack_password = ""

        # Get the Heat client
        heat = self.get_heat_client(configuration)

        # Launch the stack and wait for it to complete.
        (status,
         error_msg,
         stack,
         was_resumed) = self.launch_stack(configuration,
                                          heat,
                                          stack_run,
                                          stack_name,
                                          stack_template,
                                          reset)

        # If launch completed successfully, wait for provisioning, collect
        # its IP address, and save the private key.
        if status in UP_STATES:
            logger.info("Stack [%s] launched successfully "
                        "with status [%s]" % (stack_name, status))
            (verify_status,
             error_msg,
             stack_ip,
             stack_key,
             stack_password) = self.verify_stack(configuration,
                                                 stack,
                                                 was_resumed,
                                                 stack_name,
                                                 stack_user)

        # Roll back in case of failure: if it's a failure during creation,
        # delete the stack.  If it's a failure to resume, suspend it.
        if (status == 'CREATE_FAILED' or
            (status == 'CREATE_COMPLETE' and verify_status != 'VERIFY_COMPLETE')):  # noqa: E501
            logger.error("Deleting unsuccessfully "
                         "launched stack [%s] with status [%s] "
                         "and verify status [%s]" % (stack.id,
                                                     status,
                                                     verify_status))
            heat.stacks.delete(stack_id=stack.id)
            status = 'CREATE_FAILED'
        elif (status == 'RESUME_FAILED' or
              (status == 'RESUME_COMPLETE' and verify_status != 'VERIFY_COMPLETE')):  # noqa: E501
            logger.error("Suspending unsuccessfully "
                         "resumed stack [%s] with status [%s] "
                         "and verify status [%s]" % (stack.id,
                                                     status,
                                                     verify_status))
            heat.actions.suspend(stack_id=stack.id)
            status = 'RESUME_FAILED'

        if (status in UP_STATES and verify_status == 'VERIFY_COMPLETE'):
            logger.info("Stack [%s] verified successfully" % (stack.id))

        data = {
            'status': status,
            'error_msg': error_msg,
            'ip': stack_ip,
            'user': stack_user,
            'key': stack_key,
            'password': stack_password
        }
        return data

    def get_heat_client(self, configuration):
        return HeatWrapper(**configuration).get_client()

    def get_nova_client(self, configuration):
        return NovaWrapper(**configuration).get_client()

    def launch_stack(self,
                     configuration,
                     heat,
                     stack_run,
                     stack_name,
                     stack_template,
                     reset=False):
        """
        Launch the user stack, either by creating or resuming it.  If a reset
        is requested, delete the stack and recreate it.

        """
        status = ""
        error_msg = ""
        stack = None

        timeouts = configuration.get('task_timeouts', {})
        sleep = timeouts.get('sleep', 5)
        retries = timeouts.get('retries', 60)

        logger.info("Launching stack [%s]." % stack_name)

        new_stack = False
        was_resumed = False

        # Create the stack if it doesn't exist, resume it if it's suspended.
        try:
            logger.debug("Getting initial stack info for [%s]." % (stack_name))
            stack = heat.stacks.get(stack_id=stack_name)

            # Sleep to avoid throttling.
            time.sleep(sleep)
        except HTTPNotFound:
            # Sleep to avoid throttling.
            time.sleep(sleep)

            # Signal that we just created the stack.
            new_stack = True

            logger.info("Stack [%s] doesn't exist.  Creating it." % stack_name)
            res = heat.stacks.create(stack_name=stack_name,
                                     template=stack_template,
                                     parameters={'run': stack_run})
            stack_id = res['stack']['id']

            # Sleep to avoid throttling.
            time.sleep(sleep)

            logger.debug("Getting initial stack info for [%s]." % (stack_name))
            stack = heat.stacks.get(stack_id=stack_id)

            # Sleep to avoid throttling.
            time.sleep(sleep)

        status = stack.stack_status
        logger.debug("Got [%s] status for [%s]." % (status, stack_name))

        # If stack is undergoing a change of state, wait until it finishes.
        retry = 0
        while 'IN_PROGRESS' in status:
            if retry:
                logger.debug("Stack [%s] not ready, with status [%s]. "
                             "Waiting %s seconds until retry." % (stack_name,
                                                                  status,
                                                                  sleep))
                time.sleep(sleep)

            try:
                logger.debug("Getting stack info for [%s], "
                             "with previous status [%s]." % (stack_name,
                                                             status))
                stack = heat.stacks.get(stack_id=stack.id)
            except HTTPNotFound:
                # Sleep to avoid throttling.
                time.sleep(sleep)

                # Signal that we just created the stack.
                new_stack = True

                logger.warning("Stack [%s] disappeared "
                               "during change of state. "
                               "Re-creating it." % stack_name)
                res = heat.stacks.create(stack_name=stack_name,
                                         template=stack_template,
                                         parameters={'run': stack_run})
                stack_id = res['stack']['id']

                # Sleep to avoid throttling.
                time.sleep(sleep)

                logger.debug("Getting initial stack info "
                             "for [%s]." % (stack_name))
                stack = heat.stacks.get(stack_id=stack_id)

            status = stack.stack_status
            logger.debug("Got [%s] status for [%s]." % (status, stack_name))
            retry += 1
            if retry >= retries:
                logger.error("Stack [%s] state change [%s] "
                             "took too long.  "
                             "Giving up after %s retries" % (stack_name,
                                                             status,
                                                             retry))
                status_prefix = re.sub('_IN_PROGRESS$', '', status)
                status = '%s_FAILED' % status_prefix

        # If this is a reset request and we didn't just create it, delete the
        # stack and recreate it.
        if reset and not new_stack:
            # Sleep to avoid throttling.
            time.sleep(sleep)

            logger.info("Resetting stack [%s]." % stack_name)
            heat.stacks.delete(stack_id=stack.id)
            status = 'DELETE_IN_PROGRESS'

            # Sleep to avoid throttling.
            time.sleep(sleep)

            # Wait until delete finishes.
            retry = 0
            while ('FAILED' not in status and
                   status != 'DELETE_COMPLETE'):
                if retry:
                    logger.debug("Stack [%s] not ready, with status [%s]. "
                                 "Waiting %s seconds "
                                 "until retry." % (stack_name,
                                                   status,
                                                   sleep))
                    time.sleep(sleep)

                try:
                    logger.debug("Getting stack info for [%s], "
                                 "with previous status [%s]." % (stack_name,
                                                                 status))
                    stack = heat.stacks.get(stack_id=stack.id)
                except HTTPNotFound:
                    status = 'DELETE_COMPLETE'
                else:
                    status = stack.stack_status
                    logger.debug("Got [%s] status "
                                 "for [%s]." % (status, stack_name))
                    retry += 1
                    if retry >= retries:
                        logger.error("Stack [%s], status [%s], "
                                     "took too long to delete.  Giving up "
                                     "after %s retries" % (stack_name,
                                                           status,
                                                           retry))
                        status = 'DELETE_FAILED'

            if status == 'DELETE_COMPLETE':
                logger.info("Stack [%s] deleted successfully.  "
                            "Recreating it." % stack_name)
                res = heat.stacks.create(stack_name=stack_name,
                                         template=stack_template,
                                         parameters={'run': stack_run})
                stack_id = res['stack']['id']

                # Sleep to avoid throttling.
                time.sleep(sleep)

                logger.debug("Getting initial stack info "
                             "for [%s]." % (stack_name))
                stack = heat.stacks.get(stack_id=stack_id)

                # Sleep to avoid throttling.
                time.sleep(sleep)

                status = stack.stack_status
                logger.debug("Got [%s] status for [%s]." % (status,
                                                            stack_name))

                # Wait for stack creation
                retry = 0
                while 'IN_PROGRESS' in status:
                    if retry:
                        logger.debug("Stack [%s] not ready, with status [%s]. "
                                     "Waiting %s seconds "
                                     "until retry." % (stack_name,
                                                       status,
                                                       sleep))
                        time.sleep(sleep)

                    try:
                        logger.debug("Getting stack info for [%s], with "
                                     "previous status [%s]." % (stack_name,
                                                                status))
                        stack = heat.stacks.get(stack_id=stack.id)
                    except HTTPNotFound:
                        # Sleep to avoid throttling.
                        time.sleep(sleep)

                        logger.warning("Stack [%s] disappeared "
                                       "during change of state. "
                                       "Re-creating it." % stack_name)
                        res = heat.stacks.create(stack_name=stack_name,
                                                 template=stack_template,
                                                 parameters={'run': stack_run})
                        stack_id = res['stack']['id']

                        # Sleep to avoid throttling.
                        time.sleep(sleep)

                        logger.debug("Getting initial stack info "
                                     "for [%s]." % (stack_name))
                        stack = heat.stacks.get(stack_id=stack_id)

                    status = stack.stack_status
                    logger.debug("Got [%s] status for [%s]." % (status,
                                                                stack_name))

                    retry += 1
                    if retry >= retries:
                        logger.error("Stack [%s] state change [%s] "
                                     "took too long.  Giving up "
                                     "after %s retries" % (stack_name,
                                                           status,
                                                           retry))
                        status_prefix = re.sub('_IN_PROGRESS$', '', status)
                        status = '%s_FAILED' % status_prefix

        # If stack is suspended, resume it.
        if status == 'SUSPEND_COMPLETE':
            # Sleep to avoid throttling.
            time.sleep(sleep)

            logger.info("Resuming stack [%s]." % stack_name)
            heat.actions.resume(stack_id=stack.id)

            # Store the fact the stack was resumed
            was_resumed = True

            # Sleep to avoid throttling.
            time.sleep(sleep)

            # Wait until resume finishes.
            retry = 0
            while ('FAILED' not in status and
                   status != 'RESUME_COMPLETE'):
                if retry:
                    logger.debug("Stack [%s] not ready, with status [%s]. "
                                 "Waiting %s seconds "
                                 "until retry." % (stack_name,
                                                   status,
                                                   sleep))
                    time.sleep(sleep)

                try:
                    logger.debug("Getting stack info for [%s], "
                                 "with previous status [%s]." % (stack_name,
                                                                 status))
                    stack = heat.stacks.get(stack_id=stack.id)
                except HTTPNotFound:
                    logger.error("Stack [%s] disappeared "
                                 "during resume." % stack_name)
                    status = 'RESUME_FAILED'
                else:
                    status = stack.stack_status
                    logger.debug("Got [%s] status for [%s]." % (status,
                                                                stack_name))
                    retry += 1
                    if retry >= retries:
                        logger.error("Stack [%s], status [%s], "
                                     "took too long to resume.  Giving up"
                                     "after %s retries" % (stack_name,
                                                           status,
                                                           retry))
                        status = 'RESUME_FAILED'

        if status not in UP_STATES:
            error_msg = ("Stack [%s] launch "
                         "failed with status [%s]" % (stack_name, status))
            logger.error(error_msg)
        else:
            logger.info("Stack [%s] launch successful, "
                        "with status [%s]." % (stack_name, status))

        return (status, error_msg, stack, was_resumed)

    def verify_stack(self, configuration, stack, was_resumed, stack_name,
                     stack_user):
        """
        Fetch stack outputs, check that the stack has a public IP address, a
        private key, and is network accessible after rebooting any servers.
        Save its private key, and check that it is possible to SSH into the
        stack using it.

        """
        verify_status = 'VERIFY_COMPLETE'
        error_msg = ""
        stack_ip = None
        stack_key = ""
        stack_password = ""
        reboot_on_resume = None

        timeouts = configuration.get('timeouts', {})
        sleep = timeouts.get('sleep', 5)
        retries = timeouts.get('retries', 60)

        logger.debug("Verifying stack [%s] "
                     "network connectivity. " % (stack_name))

        for output in stack.to_dict().get('outputs', []):
            if output['output_key'] == 'public_ip':
                stack_ip = output['output_value']
                logger.debug("Found IP [%s] "
                             "for stack [%s]" % (stack_ip, stack_name))
            elif output['output_key'] == 'private_key':
                stack_key = output['output_value']
                logger.debug("Found key for stack [%s]" % (stack_name))
            elif output['output_key'] == 'password':
                stack_password = output['output_value']
                logger.debug("Found password for stack [%s]" % (stack_name))
            elif output['output_key'] == 'reboot_on_resume':
                reboot_on_resume = output['output_value']
                logger.debug("Found servers to reboot on resume "
                             "for stack [%s]" % (stack_name))

        if stack_ip is None or not stack_key:
            verify_status = 'VERIFY_FAILED'
            error_msg = ("Stack [%s] did not provide "
                         "IP and private key." % stack_name)
            logger.error(error_msg)
        else:
            if (was_resumed and
                    reboot_on_resume is not None and
                    type(reboot_on_resume) is list):
                nova = self.get_nova_client(configuration)

                for server in reboot_on_resume:
                    logger.info("Hard rebooting server [%s]" % server)
                    nova.servers.reboot(server, 'HARD')

            # Wait until stack is network accessible, but not indefinitely.
            logger.info("Waiting for stack [%s] "
                        "to become network accessible "
                        "at [%s]" % (stack_name, stack_ip))
            ping_command = "ping -c 1 -W 5 " + stack_ip + " >/dev/null 2>&1"
            for retry in range(retries):
                response = os.system(ping_command)
                if response == 0:
                    break
                else:
                    logger.debug("Could not ping stack [%s] at [%s]. "
                                 "Waiting %s seconds "
                                 "until next attempt." % (stack_name,
                                                          stack_ip,
                                                          sleep))
                    time.sleep(sleep)

            # Consider stack failed if it isn't network accessible.
            if response != 0:
                verify_status = 'VERIFY_FAILED'
                error_msg = ("Stack [%s] is not network accessible "
                             "at [%s] after %s tries." % (stack_name,
                                                          stack_ip,
                                                          retry))
                logger.error(error_msg)
            else:
                # Now wait until environment is fully provisioned.  One of the
                # requirements for the Heat template is for it to disallow SSH
                # access to the training user while provisioning is going on.
                logger.info("Checking SSH connection "
                            "for stack [%s] at [%s]" % (stack_name, stack_ip))

                ssh = paramiko.SSHClient()
                ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
                pkey = paramiko.RSAKey.from_private_key(StringIO(stack_key))

                connected = False
                for retry in range(retries):
                    try:
                        ssh.connect(stack_ip, username=stack_user, pkey=pkey)
                    except (paramiko.ssh_exception.AuthenticationException,
                            paramiko.ssh_exception.SSHException,
                            paramiko.ssh_exception.NoValidConnectionsError):
                        logger.debug("Could not SSH into stack [%s] at [%s]. "
                                     "Waiting %s seconds "
                                     "until next attempt." % (stack_name,
                                                              stack_ip,
                                                              sleep))
                        time.sleep(sleep)
                    else:
                        ssh.close()
                        connected = True
                        break

                if not connected:
                    verify_status = 'VERIFY_FAILED'
                    error_msg = ("Can't SSH into stack [%s] at [%s].  "
                                 "Giving up after %s tries." % (stack_name,
                                                                stack_ip,
                                                                retry))
                    logger.error(error_msg)
                else:
                    logger.info("Stack [%s] SSH successful "
                                "at [%s]." % (stack_name, stack_ip))

        return (verify_status,
                error_msg,
                stack_ip,
                stack_key,
                stack_password)


class CheckStudentProgressTask(Task):
    """
    Check student progress by running a set of scripts via SSH.

    """
    def run(self, configuration, tests, stack_ip, stack_user, stack_key):
        # Open SSH connection to the public facing node
        ssh = self.open_ssh_connection(configuration,
                                       stack_ip,
                                       stack_user,
                                       stack_key)

        # Run tests on the stack
        res = self.run_tests(ssh, tests)

        # Close the connection
        ssh.close()

        return res

    def run_tests(self, ssh, tests):
        sftp = ssh.open_sftp()

        # Write scripts out, run them, and keep score.
        score = 0
        for test in tests:
            # Generate a temporary filename
            script = '/tmp/.%s' % uuid.uuid4()

            # Open the file remotely and write the script out to it.
            f = sftp.open(script, 'w')
            f.write(test)
            f.close()

            # Make it executable and run it.
            sftp.chmod(script, 0o775)
            stdin, stdout, stderr = ssh.exec_command(script)
            retval = stdout.channel.recv_exit_status()
            if retval == 0:
                score += 1

            # Remove the script
            sftp.remove(script)

        return {
            'status': 'COMPLETE',
            'pass': score,
            'total': len(tests)
        }

    def open_ssh_connection(self,
                            configuration,
                            stack_ip,
                            stack_user,
                            stack_key):
        ssh = paramiko.SSHClient()
        ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())

        pkey = paramiko.RSAKey.from_private_key(StringIO(stack_key))

        ssh.connect(stack_ip, username=stack_user, pkey=pkey)

        return ssh
