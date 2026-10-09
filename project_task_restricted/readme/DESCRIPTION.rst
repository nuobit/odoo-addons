This module adds a **Restricted** checkbox to tasks. A task marked Restricted
can only be seen by the members of the **Restricted tasks** group. For everyone
else it does not exist: it is absent from every list, kanban, search, report
and RPC call, and from the customer portal, and opening it by its id or a link
raises an access error. Its messages, attachments, notification records and
customer ratings are hidden with it; a message stays readable only to its
author and to the recipients typed into it, and a notification record to the
person it notified.

Only the members of the group see the checkbox and can mark or unmark a task.
In the kanban, the card of a restricted task shows a red **Restricted** badge.

Nothing about a restricted task reaches anyone outside the group unless a
person writes it to them:

* only members can be assigned to it, have activities on it, and follow it;
* its notifications and e-mails reach the members, and the recipients a person
  typed into the message or mentioned in it, who are not made followers;
* its attachments get no download link: members open them with their own
  access;
* its changes are not reported on the tasks it blocks;
* marking a task removes its followers outside the group and the notifications
  they held on its messages, keeps its e-mails that are not delivered yet from
  reaching them, voids its portal link and its attachments' download links,
  and detaches the replies written to its messages in other conversations.

A new subtask of a restricted task is born restricted, and its creator may
untick it. A duplicated task, and the next occurrence of a recurring one, keep
the mark.

Archiving or restoring a project does the same to its restricted tasks,
whoever does it. A project that contains restricted tasks cannot be deleted,
not even by someone who sees none of them; archive it instead.

When someone leaves the group, they are taken off every restricted task they
are assigned to or follow, with an internal note on each. Before saving, the
user form and the group form warn how many tasks that concerns. Someone who
still has activities on restricted tasks cannot leave the group: saving is
refused, naming them and those tasks, until the activities are assigned to a
member or marked as done, and the forms warn of it before saving.

The restriction only removes visibility on top of the existing project access
rules; it never grants any. A project administrator outside the group does not
see restricted tasks either, in the tasks or in the Tasks Analysis and burndown
reports.
