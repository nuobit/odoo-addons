This module adds a *Job Queue User* group, which follows the job queue without
managing it.

A member of the group sees the *Job Queue* menu and, in it, the jobs: every job
of the companies they work in, whoever queued it and whatever its channel, with
its state, its dates, its result and its error. They cannot create, edit or
delete a job. The rest of the queue stays with the *Job Queue Manager*: the
*Channels* and *Job Functions* menus, and the requeue, set-to-done and cancel
actions of the job list and buttons of the job form, are not shown to a member
of the group.

Requeuing a job, setting it to done and cancelling it need the right to edit
it. *Job Queue* saves these changes with superuser rights, so without this
module any user who can read a job could change its state with a call to the
server, although the screen hides the buttons. The check applies to every
user, members of this group or not.

The check covers these three actions of *Job Queue* itself. Another module
that adds its own methods to change jobs with superuser rights is not covered:
that module has to check who calls them.

Every *Job Queue Manager* is also a *Job Queue User*.

A member of the group reads every job even when another of their groups has a
record rule that shows that group only some jobs, as the Spanish SII module
does for its users.
