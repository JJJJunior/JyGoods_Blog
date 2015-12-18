# *-*coding: utf-8 *-*

from datetime import datetime
from flask import render_template, redirect, url_for, flash, current_app, request, make_response
from app.main import main
from app.main.forms import EditProfileForm, PostForm, CommentForm
from flask.ext.login import login_required, abort, current_user  # 保护路由
from app.models import Permission
from app.decorators import admin_requird, permission_required
from app.models import User, Post, Comment
from app import db


@main.route('/', methods=['GET', 'POST'])
def index():
    form = PostForm()
    if current_user.can(Permission.WRITE_ARTICLES) and form.validate_on_submit():
        post = Post(body=form.body.data, author=current_user._get_current_object())
        db.session.add(post)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        return redirect(url_for('main.index'))

    page = request.args.get('page', 1, type=int)
    show_followed = False
    if current_user.is_authenticated:
        show_followed = bool(request.cookies.get('show_followed', ''))
    if show_followed:
        query = current_user.followed_posts
    else:
        query = Post.query
    pagination = query.order_by(
        Post.timestamp.desc()).paginate(page, per_page=current_app.config['JYGOODS_POSTS_PER_PAGE'], error_out=False)
    posts = pagination.items
    return render_template('index.html',
                           current_time=datetime.utcnow(),
                           form=form,
                           posts=posts,
                           show_followed=show_followed,
                           pagination=pagination)


@main.route('/admin')
@login_required
@admin_requird
def for_admin_only():
    return "For administrators!"


@main.route('/moderator')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def for_moderators_only():
    return "For comment moderators!"


@main.route('/user/<username>')
def user(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        abort(404)
    posts = user.posts.order_by(Post.timestamp.desc()).all()
    return render_template('user.html', user=user, posts=posts)


@main.route('/user/edit-profile', methods=['GET', 'POST'])
@login_required
def edit_profile():
    form = EditProfileForm()
    if form.validate_on_submit():
        current_user.name = form.name.data
        current_user.location = form.location.data
        current_user.about_me = form.about_me.data
        db.session.add(current_user)
        try:
            db.session.commit()
        except:
            db.session.rollback()
        flash('Your profile has been updated.')
        return redirect(url_for('main.edit_profile', username=current_user.username))
    form.name.data = current_user.name
    form.location.data = current_user.location
    form.about_me.data = current_user.about_me
    return render_template('edit_profile.html', form=form)


@main.route('/post/<int:id>', methods=['GET', 'POST'])
def post(id):
    post = Post.query.get_or_404(id)
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(body=form.body.data,
                          post=post,
                          author=current_user._get_current_object())
        db.session.add(comment)
        try:
            db.session.commit()
            flash('Your comment has been published.')
        except:
            db.session.rollback()
            flash('Submit Error, please try again.')
        return redirect(url_for('main.post', id=post.id, page=-1))
    page = request.args.get('page', 1, type=int)
    if page == -1:
        page = (post.comments.count() - 1) / current_app.config['JYGOODS_COMMENTS_PER_PAGE'] + 1
    pagination = post.comments.order_by(
        Comment.timestamp.asc()).paginate(page, per_page=current_app.config['JYGOODS_COMMENTS_PER_PAGE'],
                                          error_out=False)
    comments = pagination.items
    return render_template('post.html', posts=[post], form=form, comments=comments, pagination=pagination)


@main.route('/edit/<int:id>', methods=['GET', 'POST'])
@login_required
def edit(id):
    post = Post.query.get_or_404(id)
    if current_user.id != post.author_id and not current_user.can(Permission.ADMINISTER):
        abort(403)
    form = PostForm()
    if form.validate_on_submit():
        post.body = form.body.data
        db.session.add(post)
        try:
            db.session.commit()
            flash('The post has been updated.')
        except:
            db.session.rollback()
            flash('Error post can not update.')
        return redirect(url_for('main.post', id=post.id))
    form.body.data = post.body
    return render_template('edit_post.html', form=form)


@main.route('/follow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def follow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户')
        return redirect(url_for('main.index'))
    if current_user.is_following(user):
        flash(u'您已经关注了这位用户')
        return redirect(url_for('main.user', username=username))
    current_user.follow(user)
    flash(u'您添加了对%s的关注' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/unfollow/<username>')
@login_required
@permission_required(Permission.FOLLOW)
def unfollow(username):
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户')
        return redirect(url_for('main.index'))
    if not current_user.is_following(user):
        flash(u'您还没有关注此用户')
        return redirect(url_for('main.user', username=username))
    current_user.unfollow(user)
    flash(u'您已经取消了对%s关注' % username)
    return redirect(url_for('main.user', username=username))


@main.route('/followers/<username>')
def followers(username):
    mark = u'的关注者'
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash(u'无效的用户')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followers.paginate(page, per_page=current_app.config['JYGOODS_FOLLOWERS_PER_PAGE'],
                                         error_out=False)
    follows = [{'user': item.follower, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='Followers of',
                           endpoint='main.followers', pagination=pagination,
                           follows=follows, mark=mark)


@main.route('/followed-by/<username>')
def followed_by(username):
    mark = u'关注的用户'
    user = User.query.filter_by(username=username).first()
    if user is None:
        flash('Invalid user.')
        return redirect(url_for('main.index'))
    page = request.args.get('page', 1, type=int)
    pagination = user.followed.paginate(page, per_page=current_app.config['JYGOODS_FOLLOWERS_PER_PAGE'],
                                        error_out=False)
    follows = [{'user': item.followed, 'timestamp': item.timestamp} for item in pagination.items]
    return render_template('followers.html', user=user, title='Followers by',
                           endpoint='main.followed_by', pagination=pagination,
                           follows=follows, mark=mark)


@main.route('/all')
@login_required
def show_all():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/followed')
@login_required
def show_followed():
    resp = make_response(redirect(url_for('main.index')))
    resp.set_cookie('show_followed', '1', max_age=30 * 24 * 60 * 60)
    return resp


@main.route('/moderate')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate():
    page = request.args.get('page', 1, type=int)
    pagination = Comment.query.order_by(
        Comment.timestamp.desc()).paginate(page, per_page=current_app.config['JYGOODS_COMMENTS_PER_PAGE'],
                                           error_out=False)
    comments = pagination.items
    return render_template('moderate.html', comments=comments,
                           pagination=pagination, page=page)


@main.route('/moderate/enable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_enable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = False
    db.session.add(comment)
    try:
        db.session.commit()
    except:
        db.session.rollback()
    return redirect(url_for('main.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/moderate/disable/<int:id>')
@login_required
@permission_required(Permission.MODERATE_COMMENTS)
def moderate_disable(id):
    comment = Comment.query.get_or_404(id)
    comment.disabled = True
    db.session.add(comment)
    try:
        db.session.commit()
    except:
        db.session.rollback()
    return redirect(url_for('main.moderate', page=request.args.get('page', 1, type=int)))


@main.route('/delete/comment/<int:id>')
@login_required
@permission_required(Permission.DELETE_COMMENT)
def comment_delete(id):
    comment = Comment.query.get_or_404(id)
    db.session.delete(comment)
    try:
        db.session.commit()
    except:
        db.session.rollback()
    return redirect(url_for('main.index'))