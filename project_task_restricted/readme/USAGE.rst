To restrict a task, open it and tick **Restricted**. To list the restricted
tasks, use the **Restricted** filter of the task search; in the kanban, a red
**Restricted** badge marks them.

To write to someone outside the group about a restricted task, type them as a
recipient of the message, or mention them: they receive that message only.
*Add Followers* and *Share* refuse anyone outside the group, and name them.

To assign a restricted task, or give it an activity, to someone outside the
group, untick **Restricted** first: a restricted task accepts only members.

A program that posts on a restricted task and addresses someone outside the
group on purpose passes their partner ids in the context key
``restricted_typed_partner_ids``. Without it, they are removed from the
message, and the removal is logged.
