# coding: utf-8

"""
    views.py ~ 木犀分享视图文件

        主页: 发布分享

        /:  主页
        /share:  发布分享的页面
        /login:  登录页
        /logout: 登出页
        /new: 显示最新分享
        /hot: 显示最热分享
        /view_share: 查看分享的具体信息，评论，发表评论
"""

# models import
from . import share
from .forms import ShareForm, CommentForm
from .. import  db, app
from ..models import Share, Comment, User
# from ..auth._decorate import auth_login, auth_logout
from flask import url_for, render_template, redirect
from flask.ext.login import current_user, login_required


@share.route('/<int:page>')
@share.route('/new/<int:page>')
def index(page = 1):
    """
    muxi_share 分享你的知识

        主页，默认显示最新的分享
        添加分页，默认显示第一页

    """
    # 添加分页, share变为分页对象
    shares = Share.query.order_by('-id').paginate(page, app.config['SHARE_PER_PAGE'], False)
    for share in shares.items:
        share.content = share.share
        share.avatar = "http://7xj431.com1.z0.glb.clouddn.com/屏幕快照%202015-10-08%20下午10.28.04.png"
        share.comments = len(Comment.query.filter_by(share_id=share.id).all())
        share.author = User.query.filter_by(id=share.author_id).first().username
    return render_template('share_index.html', shares=shares)


@share.route('/hot')
def hot():
    """显示最热扩展:评论数最多的扩展"""
    hots = {}
    shares = Share.query.paginate(1, app.config['SHARE_PER_PAGE'], False)
    for share in shares.items:
        share.content = share.share
        share.comments = len(Comment.query.filter_by(share_id=share.id).all())
        share.avatar = "http://7xj431.com1.z0.glb.clouddn.com/屏幕快照%202015-10-08%20下午10.28.04.png"
        if share.comments != 0:
            hots[share] = share.comments  # 建立分享和分享评论数的关系
    sort_hots = dict(sorted(zip(hots.values(), hots.keys())))
    return render_template("share_index.html", shares=sort_hots.values()[::-1])


@share.route('/<int:id>', methods=["GET", "POST"])
def view_share(id):
    """显示特定id的分享，相关信息以及评论
       实现评论表单发表自己的评论"""
    share = Share.query.get_or_404(id)
    comments = Comment.query.filter_by(share_id=share.id).all()
    form = CommentForm()
    if form.validate_on_submit():
        comment = Comment(
            comment = form.comment.data,
            author_id = current_user.id,
            share_id = id
        )
        db.session.add(comment)
        db.session.commit()
        return redirect(url_for('share.view_share', id=id))

    share.avatar = "http://7xj431.com1.z0.glb.clouddn.com/屏幕快照%202015-10-08%20下午10.28.04.png"
    share.content = share.share
    share.comments = len(Comment.query.filter_by(share_id=share.id).all())

    for comment in comments:
        # comment.avatar = User.query.filter_by(id=comment.author_id).first().avatar
        comment.avatar = "http://7xj431.com1.z0.glb.clouddn.com/download.jpeg"
        comment.username = User.query.filter_by(id=comment.author_id).first().username
        comment.content = comment.comment
    return render_template(
        'share_second.html',
        form = form,
        share=share,
        comments=comments
    )


@login_required
@share.route('/share_send', methods=["GET", "POST"])
def add_share():
    """分享"""
    form = ShareForm()
    if form.validate_on_submit():
        share = Share(
            title = form.title.data,
            share = form.share.data,
            author_id = current_user.id
        )
        db.session.add(share)
        db.session.commit()
        return redirect(url_for('.index', page = 1))

    return render_template("share_send.html", form=form)
