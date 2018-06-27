"""create by zhouzhiyang"""

import socket
import re
import multiprocessing
import mini_web


class WebServer(object):
    """这个服务器类"""

    def __init__(self):
        """初始化tcp服务器"""
        # 1. 创建套接字
        self.tcp_server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.tcp_server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)

        # 2. 绑定
        self.tcp_server_socket.bind(("", 8866))

        # 3. 变为监听套接字
        self.tcp_server_socket.listen(128)

    def service_client(self, new_socket):
        """为这个客户端返回数据"""

        # 1. 接收浏览器发送过来的请求 ，即http请求
        # GET / HTTP/1.1
        # .....
        request = new_socket.recv(1024).decode("utf-8")
        request_lines = request.splitlines()
        print("")
        print(">" * 20)
        print(request_lines)

        # GET /index.html HTTP/1.1
        # get post put del
        file_name = ""
        ret = re.match(r"[^/]+(/[^ ]*)", request_lines[0])
        if ret:
            file_name = ret.group(1)
            # print("*"*50, file_name)
            if file_name == "/":
                file_name = "/index.html"

        # 如果是html那么会调用mini_web上的application返回页面数据
        if file_name.endswith(".html"):  # 伪静态,动态改装成静态代码,一般就是后缀改成.html

            url_params = dict()  # 给mini_web传参数的
            url_params['file_name'] = file_name

            body = mini_web.application(url_params, self.head_params)  # 调用框架处理

            head = "HTTP/1.1 %s\r\n" % self.stauts

            # 拼接我们的响应头
            for temp in self.params:
                head += "%s:%s\r\n" % temp

            content = head + "\r\n" + body

            new_socket.send(content.encode("utf-8"))



        else:
            # 返回静态的数据

            # 2. 返回http格式的数据，给浏览器

            try:
                f = open("./static" + file_name, "rb")
            except:
                response = "HTTP/1.1 404 NOT FOUND\r\n"
                response += "\r\n"
                response += "------file not found-----"
                new_socket.send(response.encode("utf-8"))
                print("文件找不到!")

            else:
                html_content = f.read()
                f.close()
                # 2.1 准备发送给浏览器的数据---header
                response = "HTTP/1.1 200 OK\r\n"
                response += "\r\n"
                # 2.2 准备发送给浏览器的数据---boy
                # response += "hahahhah"

                # 将response header发送给浏览器
                new_socket.send(response.encode("utf-8"))
                # 将response body发送给浏览器
                new_socket.send(html_content)

        # 关闭套接
        new_socket.close()

    def run_server(self):
        """用来完成整体的控制"""

        while True:
            # 4. 等待新客户端的链接
            new_socket, client_addr = self.tcp_server_socket.accept()

            # 5. 为这个客户端服务
            p = multiprocessing.Process(target=self.service_client, args=(new_socket,))
            p.start()

            new_socket.close()

        # 关闭监听套接字
        tcp_server_socket.close()

    def head_params(self, stauts, params):
        """ 把响应头存起来进行后期的拼接"""
        self.stauts = stauts
        self.params = params


def main():
    server = WebServer()
    server.run_server()


if __name__ == "__main__":
    main()
