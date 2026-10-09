* Some hour totals count the hours of restricted tasks for whoever reads them:
  on a visible parent task, *Sub-tasks Hours Spent* and the *Total Hours*,
  *Remaining Hours* and *Progress* that follow from it; on a project, its
  *Remaining Invoiced Time*. They show a number, never the task or its lines.
  Odoo stores the parent task's totals once for every reader: a total per
  reader would mean not storing them, and then lists could no longer sort or
  group by them, and *Tasks Analysis*, which reads them from the table, would
  break.
* A project's *Gross Margin*, which only analytic accounting users see, also
  counts the timesheet lines of its restricted tasks, and so does, with *Sales
  Timesheets*, the delivered quantity of a sales order line.
