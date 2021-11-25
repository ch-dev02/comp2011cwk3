from flask import render_template, flash, request, redirect, Blueprint, url_for
from app import app, db, models
from .forms import CreateTaskForm, CreateGroupForm, JoinGroupForm
import datetime
from flask_login import login_required, current_user

main = Blueprint('main', __name__)

# Default route when webpage loads - shows groups
@app.route('/groups', methods=['GET', 'POST'])
@login_required
def home(): 
    # groups = models.Group.query.all()
    # for g in groups:
    #     db.session.delete(g)
    # db.session.commit()
    UserGroups = models.UserGroup.query.filter_by(user_id=current_user.id).all()
    groups = []
    for ug in UserGroups:
        temp = models.Group.query.filter_by(id=ug.group_id).first()
        groups.append(temp)
    return render_template('groups.html',
                           page_title="Your Groups",
                           alert="You haven't joined any groups",
						   title='To-Do | Groups',
                           ret='/groups',
                           groups=groups)

# Route used to create a group
# Passes a WTForm used to validate data and create a task
# Form is also styled appropriately on page
@app.route('/create_task', methods=['GET', 'POST'])
@login_required
def create_task():
    form = CreateTaskForm()
    UserGroups = models.UserGroup.query.filter_by(user_id=current_user.id).all()
    groups = []
    for ug in UserGroups:
        temp = models.Group.query.filter_by(id=ug.group_id).first()
        groups.append(temp)

    if len(UserGroups) == 0:
        flash('You must join a group before creating a task', 'error')
        app.logger.error('User %d tried to create a task without joining a group', current_user.id)
        return redirect('/create_group')
    form.group.choices = [(g.id, g.name) for g in groups]
    if request.method == 'POST' and form.validate():
        t = models.Task(title=form.title.data,deadline=form.date.data,description=form.description.data,complete=False, group_id=form.group.data)
        db.session.add(t)
        db.session.commit()
        flash('Succesfully Created The Task')
    return render_template('create_task.html',
                           title='To-Do | Create A Task',
                           form=form)

# Route used to create a group
# Passes a WTForm used to validate data and create a group
# Form is also styled appropriately on page
@app.route('/create_group', methods=['GET', 'POST'])
@login_required
def create_group():
    form = CreateGroupForm()
    if request.method == 'POST' and form.validate():
        taken = models.Group.query.filter_by(code=form.code.data).first()
        if taken:
            flash('Group Code Taken', 'error')
            return render_template('create_group.html',
                                   title='To-Do | Create A Group',
                                   form=form)
        t = models.Group(name=form.name.data,code=form.code.data)
        db.session.add(t)
        db.session.commit
        a = models.Group.query.filter_by(code=form.code.data).first()
        ug = models.UserGroup(user_id=current_user.id,group_id=a.id)
        db.session.add(ug)
        db.session.commit()
        flash('Succesfully Created And Joined The Group')
    return render_template('create_group.html',
                           title='To-Do | Create A Group',
                           form=form)

# Similar to the '/' route however when querying the database 
# only searches tasks marked complete=false
# before outputing tasks it changes the deadline to custom
# output formatting
@app.route('/tasks', methods=['GET', 'POST'])
@login_required
def tasks():
    gid = request.args["gid"]
    user = models.User.query.filter_by(id=current_user.id).first()
    ug = models.UserGroup.query.filter_by(group_id=gid,user_id=user.id).first()
    if not ug:
        flash('You are not a member of this group', 'error')
        app.logger.warning("Requested List of Tasks for group: " + str(gid) + " but user: " + str(user.username) + " is not a member of this group")
        return redirect('/')
    group = models.Group.query.filter_by(id=gid).first()
    if not group:
        flash('Group Not Found', 'error')
        app.logger.error("Requested List of Tasks for group: " + str(gid) + " but group does not exist")
        return redirect('/')
    tasks = models.Task.query.filter_by(group_id=gid).all()
    for task in tasks:
        task.deadline = task.deadline.strftime("%d-%m-%Y")
    return render_template('tasks.html',
                           page_title=group.name+" Tasks",
                           alert="No tasks available",
                           title='To-Do | Tasks', 
                           ret='/tasks?gid='+gid,
                           tasks=tasks,
                           join_code=group.code)

# This route is used to change a task to complete=true
# is triggered by a form with method=GET
# it is passed the task id and page request was sent from
# this is then used to change the task and return to page
@app.route('/mark_complete', methods=['GET'])
@login_required
def mark_complete():
    task_id = request.args["id"]
    current_page = request.args["current_page"]
    t = models.Task.query.get(task_id)
    ug = models.UserGroup.query.filter_by(group_id=t.group_id,user_id=current_user.id).first()
    if not ug:
        flash('You are not a member of this group', 'error')
        app.logger.warning("Requested to mark task: " + str(task_id) + " as complete but user: " + str(current_user.username) + " is not a member of this group")
        return redirect('/')
    t.complete = True
    db.session.commit()
    return redirect(current_page)

# This route is used to delete a task this
# is triggered by a form with method=GET
# it is passed the task id and page request was sent from
# this is then used to delete the task and return to page
@app.route('/delete', methods=['GET'])
@login_required
def delete():
    task_id = request.args["id"]
    current_page = request.args["current_page"]
    t = models.Task.query.get(task_id)
    ug = models.UserGroup.query.filter_by(group_id=t.group_id,user_id=current_user.id).first()
    if not ug:
        flash('You are not a member of this group', 'error')
        app.logger.warning("Requested to delete task: " + str(task_id) + " but user: " + str(current_user.username) + " is not a member of this group")
        return redirect('/')
    db.session.delete(t)
    db.session.commit()
    return redirect(current_page)

@app.route('/join_group', methods=['GET', 'POST'])
@login_required
def join():
    form = JoinGroupForm()
    if request.method == 'POST' and form.validate():
        exist = models.Group.query.filter_by(code=form.code.data).first()
        if not exist:
            flash('Group Code Not Found', 'error')
            app.logger.warning("Requested to join group: " + str(form.code.data) + " but group does not exist")
            return render_template('join_group.html',
                                   title='To-Do | Join A Group',
                                   form=form)
        ug = models.UserGroup.query.filter_by(group_id=exist.id,user_id=current_user.id).first()
        if ug:
            flash('You are already a member of this group', 'error')
            app.logger.warning("Requested to join group: " + str(form.code.data) + " but user: " + str(current_user.username) + " is already a member of this group")
            return render_template('join_group.html',
                                      title='To-Do | Join A Group',
                                      form=form)
        nug = models.UserGroup(user_id=current_user.id,group_id=exist.id)
        db.session.add(nug)
        db.session.commit()
        flash('Succesfully Joined The Group')
    return render_template('join_group.html',
                           title='To-Do | Join A Group',
                           form=form)

# This route is used to delete a task this
# is triggered by a form with method=GET
# it is passed the task id and page request was sent from
# this is then used to delete the task and return to page
@app.route('/leave', methods=['GET'])
@login_required
def leave():
    gid = request.args["gid"]
    ug = models.UserGroup.query.filter_by(group_id=gid,user_id=current_user.id).first()
    if not ug:
        flash('You are not a member of this group', 'error')
        app.logger.warning("Requested to leave group: " + str(gid) + " but user: " + str(current_user.username) + " is not a member of this group")
        return redirect('/')
    db.session.delete(ug)
    db.session.commit()
    ugs = models.UserGroup.query.filter_by(group_id=gid).all()
    if len(ugs) == 0:
        app.logger.info("Delete group: " + str(gid) + " as no members remain")
        group = models.Group.query.filter_by(id=gid).first()
        db.session.delete(group)
        db.session.commit()
    return redirect('/')