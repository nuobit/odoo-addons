* The name of a restricted task stays visible where another record points to
  it: the *Parent Task* of a visible subtask, and the notifications of its
  messages that someone outside the group received. Opening it gives an access
  error. Do not put an amount in a task's name.
* The document count of a project includes the attachments of its restricted
  tasks; opening them is refused.
* The superuser, and an administrator who becomes superuser in debug mode,
  see every task.
* E-mails already delivered when a task is marked are not recalled.
* A member who leaves the group keeps the notifications they received while
  they were a member, and can still read those messages.
* A reply received by e-mail keeps the contacts of its To and Cc as its
  addressees, also outside the group: they can read that message, which they
  received.
* A module installed later that adds notification recipients above this
  module's filter is not filtered, nor is code that changes the recipients of
  an existing message.
* Uninstalling the module makes every restricted task visible again.
