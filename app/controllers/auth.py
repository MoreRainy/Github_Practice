# 认证相关 controller(登录/注册/退出)

import tornado.web

from app.controllers.base import BaseHandler
from app.models.user import UserRepository


class LoginHandler(BaseHandler):
	def get(self):
		login_type = self.get_argument("type", "user")
		if login_type not in ("user", "admin"):
			login_type = "user"
		self.render("login.html", title="登录", error=None, login_type=login_type)

	def post(self):
		username = (self.get_body_argument("username", "") or "").strip()
		password = self.get_body_argument("password", "")
		login_type = self.get_body_argument("login_type", "user")
		if login_type not in ("user", "admin"):
			login_type = "user"

		if not username or not password:
			self.set_status(400)
			return self.render("login.html", title="登录", error="用户名或密码不能为空", login_type=login_type)

		user = UserRepository.get_user_by_username(username)
		if not user or not UserRepository.verify_user(username, password):
			self.set_status(401)
			return self.render("login.html", title="登录", error="用户名或密码错误", login_type=login_type)

		role_code = UserRepository.get_role_code(user)
		is_admin = UserRepository.is_admin_role(role_code)
		is_normal_user = UserRepository.is_normal_user_role(role_code)

		if login_type == "admin":
			if not is_admin:
				self.set_status(403)
				return self.render("login.html", title="登录", error="该账号不是管理员，请使用普通用户入口登录", login_type=login_type)
		else:
			if not is_normal_user:
				self.set_status(403)
				return self.render("login.html", title="登录", error="该账号不是普通用户，请使用管理员入口登录", login_type=login_type)

		self.set_secure_cookie("username", username)
		if login_type == "admin":
			self.redirect("/admin/users")
		else:
			self.redirect("/")


class LogoutHandler(BaseHandler):
	def post(self):
		self.clear_cookie("username")
		self.redirect("/auth/login")
