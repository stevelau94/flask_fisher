import json

from flask import jsonify, request, render_template, flash
from flask_login import current_user

from app.forms.book import SearchForm
from app.models.gift import Gift
from app.models.wish import Wish
from app.view_models.book import BookViewModel, BookCollection
from app.view_models.trade import TradeInfo
from app.web import web
from app.lib.helper import is_isbn_or_key
from app.spider.yushu_book import YuShuBook


@web.route('/book/search')
def search():
    # 注意验证层
    form = SearchForm(request.args)
    book = BookCollection()

    if form.validate():
        q = form.q.data.strip()
        page = form.page.data
        print(q, page)
        isbn_or_key = is_isbn_or_key(q)
        yushu_book = YuShuBook()

        if isbn_or_key == "isbn":
            yushu_book.isbnSearch(q)
        else:
            yushu_book.keySearch(q)

        book.fill(yushu_book, q)
        # return json.dumps(book,default=lambda obj:obj.__dict__)

    else:
        flash('关键字错误，请重新输入关键字')
        # return jsonify(form.errors)

    return render_template('search_result.html', books=book)


@web.route('/book/<isbn>/detail')
def book_detail(isbn):
    # 分三种情况
    # 1. 判断是否已经赠送当前书籍
    # 2. 判断是否已经索要当前书籍
    # 3. 判断是否既不赠送也不索要当前书籍
    # 两个False是第三种情况
    has_in_gifts = False
    has_in_wishes = False

    # 如果登陆了，判断 1 2情况
    if current_user.is_authenticated:
        if Gift.query.filter_by(uid=current_user.id, isbn=isbn, launched=False).first():
            has_in_gifts = True
        if Wish.query.filter_by(uid=current_user.id, isbn=isbn, launched=False).first():
            has_in_wishes = True

    # 书籍详情信息
    yushubook = YuShuBook()
    yushubook.isbnSearch(isbn)
    book = BookViewModel(yushubook.first)

    # 获取赠送列表和心愿列表
    gifts = Gift.query.filter_by(isbn=isbn, launched=False).all()
    wishes = Wish.query.filter_by(isbn=isbn, launched=False).all()

    trade_gitfs = TradeInfo(gifts)
    trade_wishes = TradeInfo(wishes)

    return render_template('book_detail.html', book=book, gifts=trade_gitfs, wishes=trade_wishes,
                           has_in_gifts=has_in_gifts, has_in_wishes=has_in_wishes)
