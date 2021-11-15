from discord.ext.commands import command, Cog
from bot import helpers

class TaskCog(Cog):
    def __init__(self, bot, task_service):
        self._bot = bot
        self._task_service = task_service


    def __draw_task_table__(self, tasks):
        if tasks:
            user_ids = set([t.user_id for t in tasks])
            user_ids = sorted([uid for uid in user_ids], key=lambda uid: self._bot.get_user(uid).name if uid is not None else '')

            columns = [{'attr': 'seq_no'},
                       {'attr': 'priority'},
                       {'attr': 'title'}]

            s = ''
            if helpers.prepare_table_columns(columns, tasks):
                for uid in user_ids:
                    if uid:
                        s += 'Tasks assigned to {}\n'.format(helpers.format_user(self._bot, uid))
                    else:
                        s += 'Unassigned tasks'

                    user_tasks = [t for t in tasks if t.user_id == uid]
                    user_tasks = sorted(user_tasks, key=lambda t: (t.priority or 999999, t.title))
                    s += helpers.draw_table(columns, user_tasks)
            else:
                s = 'I\'m having trouble displaying this table for some reason...'
        else:
            s = 'There are no matching tasks.'

        return s


    @command(name='t-add', help='(title, [priority]) Adds a task and assigns it to the requesting user')
    async def t_add(self, context, title, priority=None):
        priority = helpers.parse_int_param(priority, False, False)
        t, msg = self._task_service.add_task(context.channel.id, title, context.author.id, priority, context.author.id)

        if msg:
            await context.send(msg)
        elif t:
            await context.send('Your task has been added.')
        else:
            await context.send('Something went wrong while processing your request.')


    @command(name='t-add-shared', help='(title, [priority]) Adds an unassigned task')
    async def t_add_shared(self, context, title, priority=None):
        priority = helpers.parse_int_param(priority, False, False)
        t, msg = self._task_service.add_task(context.channel.id, title, None, priority, context.author.id)

        if msg:
            await context.send(msg)
        elif t:
            await context.send('The task has been added.')
        else:
            await context.send('Something went wrong while processing your request.')


    @command(name='t-claim', help='(seq_no) Assigns a task to the requesting user')
    async def t_claim(self, context, seq_no):
        seq_no = helpers.parse_int_param(seq_no, False, False)

        if seq_no:
            t, msg = self._task_service.assign_task(context.channel.id, seq_no, context.author.id, context.author.id)

            if msg:
                await context.send(msg)
            elif t:
                await context.send('{} has claimed the task \'{}\'.'.format(helpers.format_user(self._bot, t.user_id), t.title))
            else:
                await context.send('Something went wrong while processing your request.')
        else:
            await context.send('Invalid input.')


    @command(name='t-clear-priority', help='(seq_no) Removes the priority of a task')
    async def t_clear_priority(self, context, seq_no):
        seq_no = helpers.parse_int_param(seq_no, False, False)

        if seq_no:
            t, msg = self._task_service.set_task_priority(context.channel.id, seq_no, None, context.author.id)

            if msg:
                await context.send(msg)
            elif t:
                await context.send('The priority for task \'{}\' has been cleared.'.format(t.title))
            else:
                await context.send('Something went wrong while processing your request.')
        else:
            await context.send('Invalid input.')


    @command(name='t-condense', help='(none) Condenses the task sequence numbers')
    async def t_condense(self, context):
        tasks, msg = self._task_service.condense(context.channel.id, context.author.id)

        if msg:
            await context.send(msg)
        elif tasks:
            await context.send('Task sequence numbers have been successfully condensed.')
        else:
            await context.send('Something went wrong while processing your request.')


    @command(name='t-release', help='(seq_no) Unassigns a task from the requesting user')
    async def t_release(self, context, seq_no):
        seq_no = helpers.parse_int_param(seq_no, False, False)

        if seq_no:
            t, msg = self._task_service.assign_task(context.channel.id, seq_no, None, context.author.id)

            if msg:
                await context.send(msg)
            elif t:
                await context.send('{} has released the task \'{}\'.'.format(helpers.format_user(self._bot, context.author.id), t.title))
            else:
                await context.send('Something went wrong while processing your request.')
        else:
            await context.send('Invalid input.')


    @command(name='t-remove', help='(seq_no) Removes a task')
    async def t_remove(self, context, seq_no):
        seq_no = helpers.parse_int_param(seq_no, False, False)

        if seq_no:
            t, msg = self._task_service.remove_task(context.channel.id, seq_no, context.author.id)

            if msg:
                await context.send(msg)
            elif t:
                await context.send('The task \'{}\' has been removed.'.format(t.title))
            else:
                await context.send('Something went wrong while processing your request.')
        else:
            await context.send('Invalid input.')


    @command(name='t-remove-mine', help='(none) Removes all tasks assigned to the requesting user')
    async def t_remove_mine(self, context):
        tasks, msg = self._task_service.remove_tasks(context.channel.id, context.author.id, context.author.id)

        if msg:
            await context.send(msg)
        elif tasks:
            await context.send('{} tasks have been removed.'.format(len(tasks)))
        else:
            await context.send('Something went wrong while processing your request.')


    @command(name='t-remove-shared', help='(none) Removes all unassigned tasks')
    async def t_remove_shared(self, context):
        tasks, msg = self._task_service.remove_tasks(context.channel.id, None, context.author.id)

        if msg:
            await context.send(msg)
        elif tasks:
            await context.send('{} tasks have been removed.'.format(len(tasks)))
        else:
            await context.send('Something went wrong while processing your request.')


    @command(name='t-set-priority', help='(seq_no, priority) Sets the priority of a task')
    async def t_set_priority(self, context, seq_no, priority):
        seq_no = helpers.parse_int_param(seq_no, False, False)
        priority = helpers.parse_int_param(priority, False, False)

        if seq_no and priority:
            t, msg = self._task_service.set_task_priority(context.channel.id, seq_no, priority, context.author.id)

            if msg:
                await context.send(msg)
            elif t:
                await context.send('The priority for task \'{}\' has been set to {}.'.format(t.title, t.priority))
            else:
                await context.send('Something went wrong while processing your request.')
        else:
            await context.send('Invalid input.')


    @command(name='t-set-title', help='seq_no, title) Sets the title of a task')
    async def t_set_title(self, context, seq_no, title):
        seq_no = helpers.parse_int_param(seq_no, False, False)

        if seq_no and title:
            t, msg = self._task_service.set_task_title(context.channel.id, seq_no, title, context.author.id)

            if msg:
                await context.send(msg)
            elif t:
                await context.send('The title for this task has been set to \'{}\'.'.format(t.title))
            else:
                await context.send('Something went wrong while processing your request.')
        else:
            await context.send('Invalid input.')


    @command(name='t-view', help='(none) Views unassigned tasks and tasks assigned to the requesting user')
    async def t_view(self, context):
        tasks, msg = self._task_service.get_tasks(context.channel.id, False, [None, context.author.id], context.author.id)

        if msg:
            await context.send(msg)
        else:
            await context.send(self.__draw_task_table__(tasks))


    @command(name='t-view-all', help='(none) Views all tasks')
    async def t_view_all(self, context):
        tasks, msg = self._task_service.get_tasks(context.channel.id, True, None, context.author.id)

        if msg:
            await context.send(msg)
        else:
            await context.send(self.__draw_task_table__(tasks))
