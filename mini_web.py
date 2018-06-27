"""create by zhouzhiyang"""

# 服务器给数据,返回数据给服务器
import re

from urllib.request import unquote  # 解码

# 定义空字典,用来存储路径跟对应的函数引用
from pymysql import connect

# 这个是路径跟方法的函数
url_dict = dict()


# start_response用来框架给服务器传响应头的数据
# environ用来得到服务器传过来的文件路径
def application(environ, start_response):
    """返回具体展示的界面给服务器"""
    start_response('200 OK', [('Content-Type', 'text/html;charset=utf-8')])  # 返回响应头

    # 根据不同的地址进行判断
    file_name = environ['file_name']

    for key, value in url_dict.items():
        match = re.match(key, file_name)  # 你的地址跟你的规则一致

        if match:
            # 匹配了
            return value(match)  # 调用匹配到的函数引用,返回匹配的页面内容

    else:
        # 说明没找到
        return "not page is find!"


# 这个装饰器传参,用来完成路由的功能
def route(url_address):  # url_address表示页面的路径
    """主要的目的自动添加路径跟匹配的函数到我们的url字典中"""

    def set_fun(func):
        def call_fun(*args, **kwargs):
            return func(*args, **kwargs)

        # 根据不同的函数名称去添加到字典中
        url_dict[url_address] = call_fun

        return call_fun

    return set_fun


#################################################上面是框架部分#############################################

# 一个功能一个函数 ,一个页面一个函数
# 框架让我们只需要关系页面展示什么

# 写一个首页
@route("/index.html")
def index(match):
    # 打开
    with open("./templates/index.html") as f:
        content = f.read()

    # 从数据库拿到数据
    # 连接数据库
    # 创建Connection连接
    conn = connect(host='localhost', port=3306, database='stock_db', user='root', password='mysql', charset='utf8')
    # 获得Cursor对象
    cs1 = conn.cursor()

    # 执行sql语句
    sql = """ select * from info;"""
    cs1.execute(sql)
    # 得到数据
    rows_data = cs1.fetchall()

    # 关闭
    cs1.close()
    conn.close()

    row_str = """<tr>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>%s</td>
        <td>
            <input type="button" value="添加" id="toAdd" name="toAdd" systemidvaule="%s">
        </td>
        </tr>"""

    # 有多行数据根据数据库查询出来的进行拼接
    # 表格字符串
    table_str = ""
    for temp in rows_data:
        table_str += row_str % (temp[0], temp[1], temp[2], temp[3], temp[4], temp[5], temp[6], temp[7], temp[1])

    # 使用正则去替换们的数据{%content%}替换成row_str
    new_content = re.sub(r'\{%content%\}', table_str, content)  # 生成一个新的内容

    # 返回
    # return content
    return new_content  # 返回新的界面


# 个人中心

@route(r"/center.html")
def center(match):
    # 拿到前端的界面
    # 拿到数据库的数据
    # 拼接数据
    # 返回拼接完的数据

    # 拿到前端的数据
    with open("./templates/center.html") as f:
        content = f.read()

    # 从数据库拿到数据
    # 连接数据库
    # 创建Connection连接
    conn = connect(host='localhost', port=3306, database='stock_db', user='root', password='mysql', charset='utf8')
    # 获得Cursor对象
    cs1 = conn.cursor()

    # 执行sql语句
    sql = """ select info.code,info.short,info.chg,info.turnover,info.price,info.highs,focus.note_info from info inner join focus on info.id = focus.info_id; """
    cs1.execute(sql)

    # 得到数据
    rows_data = cs1.fetchall()

    # 关闭
    cs1.close()
    conn.close()

    # 拼接数据
    # 假的一行数据
    row_str = """<tr>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>%s</td>
            <td>
                <a type="button" class="btn btn-default btn-xs" href="/update/%s.html"> <span class="glyphicon glyphicon-star" aria-hidden="true"></span> 修改 </a>
            </td>
            <td>
                <input type="button" value="删除" id="toDel" name="toDel" systemidvaule="%s">
            </td>
        </tr>"""
    # 根据数据库的循环去拼接真实的一行
    # 表格的字符串
    table_str = ""
    for temp in rows_data:
        table_str += row_str % (temp[0], temp[1], temp[2], temp[3], temp[4], temp[5], temp[6], temp[0], temp[0])

    content = re.sub(r'\{%content%\}', table_str, content)

    return content  # 展示 拼接完的内容


@route(r'/add/(\d+).html')  # 让所有的添加操作都 到这个方法 中
def add(match):
    # 得到我们的code代码
    code = match.group(1)

    # 如果数据已经 存在,那么提示已添加 ,如果不存在,那么添加,并提示添加成功
    # 操作数据判断是否存在这个数据在focus表
    # 连接数据
    # 创建Connection连接
    conn = connect(host='localhost', port=3306, database='stock_db', user='root', password='mysql', charset='utf8')
    # 获得Cursor对象
    cs1 = conn.cursor()

    # 查询数据
    sql = """ select * from focus where info_id = (select id from info where code = %s);"""
    cs1.execute(sql, (code,))  # sql参数化传参

    # 判断是否有数据
    if cs1.fetchone():
        # 说明数据
        # 提示已存在
        # 返回 之前要关闭资源
        cs1.close()
        conn.close()
        return "亲,已关注过了!"
    else:
        # 没有添加过,添加数据并提示
        add_sql = "insert into focus(info_id) (select id from info where code = %s);"
        cs1.execute(add_sql, (code,))
        # 提交
        conn.commit()
        # 关闭
        cs1.close()
        conn.close()
        return "添加成功了"


# 删除个人中心的数据
# /del/000007.html

@route("/del/(\d+).html")
def del_method(match):
    # code

    code = match.group(1)

    # 通过数据库删除数据
    # 连接
    # 创建Connection连接
    conn = connect(host='localhost', port=3306, database='stock_db', user='root', password='mysql', charset='utf8')
    # 获得Cursor对象
    cs1 = conn.cursor()

    # 执行sql
    sql = """delete from focus where info_id = (select id from info where code = %s);"""  # TODO:后面再写sql
    cs1.execute(sql, (code,))
    # 提交
    conn.commit()
    # 关闭
    cs1.close()
    conn.close()

    return "删除成功"


# 更新界面展示
@route("/update/(\d+).html")
def update_page(match):
    # 展示更新的界面
    with open("./templates/update.html") as f:
        content = f.read()

    # 替换我们的code
    code = match.group(1)
    # code替换
    content_new = re.sub(r"\{%code%\}", code, content)

    # 得到备注的信息
    # 通过 数据 库拿到
    # 连接数据库
    # 创建Connection连接
    conn = connect(host='localhost', port=3306, database='stock_db', user='root', password='mysql', charset='utf8')
    # 获得Cursor对象
    cs1 = conn.cursor()

    # 执行sql语句
    sql = """select note_info from focus where info_id = (select id from info where code = %s);"""
    cs1.execute(sql, (code,))

    rows_data = cs1.fetchall()
    print(rows_data[0][0])  # (('23234234',),)

    # 替换备注的信息
    content_new_2 = re.sub(r'\{%note_info%\}', rows_data[0][0], content_new)

    return content_new_2


# 更新界面内容
# 让所有的更新都到这个方法 中
@route(r'/update/(\d+)/(.*)\.html')
def update_data(match):
    # 得到code
    code = match.group(1)
    # 内容
    # 解码内容
    note = unquote(match.group(2))

    print(code, "---->", note)

    # 操作数据库更新数据
    # 连接
    # 创建Connection连接
    conn = connect(host='localhost', port=3306, database='stock_db', user='root', password='mysql', charset='utf8')
    # 获得Cursor对象
    cs1 = conn.cursor()

    # 执行sql
    sql = """ update focus set note_info = %s where info_id = (select id from info where code = %s);"""
    cs1.execute(sql, (note, code))

    # 提交
    conn.commit()
    # 关闭
    cs1.close()
    conn.close()

    return "更新成功"
