from discord.ext.commands import command, Cog
from bot import helpers

class TaskCog(Cog):
    def __init__(self, bot, task_service):
        self._bot = bot
        self._task_service = task_service


    async def __draw_task_table__(self, tasks):
        if tasks:
            user_ids = set([t.user_id for t in tasks])
            users = [(uid, await helpers.get_user_string(self._bot, uid)) for uid in user_ids]
            users.sort(key=lambda u: u[1])

            columns = [{"attr": "task_id", "header": "id", "align": "right"},
                       {"attr": "priority", "align": "right"},
                       {"attr": "description", "header": "descr"}]

            s = ""
            if helpers.prepare_table_columns(columns, tasks):
                for uid, _ in users:
                    if uid:
                        s += f"Tasks assigned to {await helpers.format_user(self._bot, uid)}\n"
                    else:
                        s += "Unassigned tasks"

                    user_tasks = [t for t in tasks if t.user_id == uid]
                    user_tasks = sorted(user_tasks, key=lambda t: (t.priority or 999999, t.description))
                    s += helpers.draw_table(columns, user_tasks)
            else:
                s = "I'm having trouble displaying this table for some reason..."
        else:
            s = "There are no matching tasks."

        return s


    @command(name="t-add", help="(descr, [priority]) Adds a task and assigns it to the requesting user")
    async def t_add(self, context, description, priority=None):
        priority = helpers.parse_int_param(priority, False, False)
        t, msg = self._task_service.add_task(context.channel.id, description, context.author.id, priority)

        if msg:
            await context.send(msg)
        elif t:
            await context.send("Your task has been added.")
        else:
            await context.send("Something went wrong while processing your request.")


    @command(name="t-add-shared", help="(descr, [priority]) Adds an unassigned task")
    async def t_add_shared(self, context, description, priority=None):
        priority = helpers.parse_int_param(priority, False, False)
        t, msg = self._task_service.add_task(context.channel.id, description, None, priority)

        if msg:
            await context.send(msg)
        elif t:
            await context.send("The task has been added.")
        else:
            await context.send("Something went wrong while processing your request.")


    @command(name="t-claim", help="(id) Assigns a task to the requesting user")
    async def t_claim(self, context, task_id):
        task_id = helpers.parse_int_param(task_id, False, False)

        if task_id:
            t, msg = self._task_service.assign_task(task_id, context.author.id, context.author.id)

            if msg:
                await context.send(msg)
            elif t:
                await context.send(f"{helpers.format_user(self._bot, t.user_id)} has claimed the task '{t.description}'.")
            else:
                await context.send("Something went wrong while processing your request.")
        else:
            await context.send("Invalid input.")


    @command(name="t-clear-pri", help="(id) Removes the priority of a task", aliases=("t-clear-priority",))
    async def t_clear_priority(self, context, task_id):
        task_id = helpers.parse_int_param(task_id, False, False)

        if task_id:
            t, msg = self._task_service.set_task_priority(task_id, None, context.author.id)

            if msg:
                await context.send(msg)
            elif t:
                await context.send(f"The priority for task '{t.description}' has been cleared.")
            else:
                await context.send("Something went wrong while processing your request.")
        else:
            await context.send("Invalid input.")


    @command(name="t-release", help="(id) Unassigns a task from the requesting user")
    async def t_release(self, context, task_id):
        task_id = helpers.parse_int_param(task_id, False, False)

        if task_id:
            t, msg = self._task_service.assign_task(task_id, None, context.author.id)

            if msg:
                await context.send(msg)
            elif t:
                await context.send(f"{helpers.format_user(self._bot, context.author.id)} has released the task '{t.description}'.")
            else:
                await context.send("Something went wrong while processing your request.")
        else:
            await context.send("Invalid input.")


    @command(name="t-rmv", help="(id) Removes a task", aliases=("t-remove",))
    async def t_remove(self, context, task_id):
        task_id = helpers.parse_int_param(task_id, False, False)

        if task_id:
            t, msg = self._task_service.remove_task(task_id, context.author.id)

            if msg:
                await context.send(msg)
            elif t:
                await context.send(f"The task '{t.description}' has been removed.")
            else:
                await context.send("Something went wrong while processing your request.")
        else:
            await context.send("Invalid input.")


    @command(name="t-rmv-mine", help="(none) Removes all tasks assigned to the requesting user", aliases=("t-remove-mine",))
    async def t_remove_mine(self, context):
        tasks, msg = self._task_service.remove_tasks(context.author.id)

        if msg:
            await context.send(msg)
        elif tasks:
            await context.send(f"{len(tasks)} tasks have been removed.")
        else:
            await context.send("Something went wrong while processing your request.")


    @command(name="t-rmv-shared", help="(none) Removes all unassigned tasks", aliases=("t-remove-shared",))
    async def t_remove_shared(self, context):
        tasks, msg = self._task_service.remove_tasks(None)

        if msg:
            await context.send(msg)
        elif tasks:
            await context.send(f"{len(tasks)} tasks have been removed.")
        else:
            await context.send("Something went wrong while processing your request.")


    @command(name="t-set-pri", help="(id, priority) Sets the priority of a task", aliases=("t-set-priority",))
    async def t_set_priority(self, context, task_id, priority):
        task_id = helpers.parse_int_param(task_id, False, False)
        priority = helpers.parse_int_param(priority, False, False)

        if task_id and priority:
            t, msg = self._task_service.set_task_priority(task_id, priority, context.author.id)

            if msg:
                await context.send(msg)
            elif t:
                await context.send(f"The priority for task '{t.description}' has been set to {t.priority}.")
            else:
                await context.send("Something went wrong while processing your request.")
        else:
            await context.send("Invalid input.")


    @command(name="t-set-descr", help="(id, descr) Sets the description of a task", aliases=("t-set-description",))
    async def t_set_title(self, context, task_id, description):
        task_id = helpers.parse_int_param(task_id, False, False)

        if task_id and description:
            t, msg = self._task_service.set_task_title( task_id, description, context.author.id)

            if msg:
                await context.send(msg)
            elif t:
                await context.send(f"The description for this task has been set to '{t.description}'.")
            else:
                await context.send("Something went wrong while processing your request.")
        else:
            await context.send("Invalid input.")


    @command(name="t-vw", help="(none) Views unassigned tasks and tasks assigned to the requesting user", aliases=("t-view",))
    async def t_view(self, context):
        tasks, msg = self._task_service.get_tasks(context.channel.id, False, [None, context.author.id])

        if msg:
            await context.send(msg)
        else:
            await context.send(await self.__draw_task_table__(tasks))


    @command(name="t-vw-all", help="(none) Views all tasks", aliases=("t-view-all",))
    async def t_view_all(self, context):
        tasks, msg = self._task_service.get_tasks(context.channel.id, True, None)

        if msg:
            await context.send(msg)
        else:
            await context.send(await self.__draw_task_table__(tasks))
