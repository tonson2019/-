#导入库
import os 
import sqlite3
import tkinter as tk
from tkinter import messagebox

#配置常量
WIDTH = 1000
HEIGHT = 600
PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

#生成控制器controller
class App(tk.Tk):
    def frame_show(self, window):
        frame = self.frame_dict[window]
        frame.tkraise()

    def __init__(self):
        super().__init__()
        self.data_execute = DataExecute()
        
        self.title("学生信息管理系统")
        self.geometry(f"{WIDTH}x{HEIGHT}")

        container = tk.Frame(self)
        container.pack(fill="both", expand=True)

        self.frame_dict = {}

        for F in [MainWindow, StudentWindow, AdminWindow]:
            frame = F(container, self.data_execute, self)
            frame.place(x=0, y=0, width=WIDTH, height=HEIGHT)
            self.frame_dict[F] = frame

        self.frame_show(MainWindow)
    
#数据管理操作工具
class DataExecute():
    def init_table(self):
        sql_student = """
        CREATE TABLE IF NOT EXISTS student(
        user_name TEXT PRIMARY KEY,
        password TEXT NOT NULL
        )
        """        

        sql_admin = """
        CREATE TABLE IF NOT EXISTS admin(
        user_name TEXT PRIMARY KEY,
        password TEXT NOT NULL
        )
        """        

        sql_score = """
        CREATE TABLE IF NOT EXISTS score(
        student_name TEXT PRIMARY KEY,
        chinese REAL,
        math REAL,
        english REAL
        )
        """   
        self.execute_sql(sql_student)
        self.execute_sql(sql_admin)
        self.execute_sql(sql_score) 

    def __init__(self):
        if not os.path.exists(PATH):
            os.makedirs(PATH)
        self.path = os.path.join(PATH, "studentinfo.db")
        self.init_table()

    def get_conn(self):
        return sqlite3.connect(self.path)

    def execute_sql(self, sql, param=()):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute(sql, param)
        conn.commit()
        cur.close()
        conn.close()

    def fetch_one(self, sql, param=()):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute(sql, param)
        result = cur.fetchone()
        cur.close()
        conn.close()
        return result

    def fetch_all(self, sql, param=()):
        conn = self.get_conn()
        cur = conn.cursor()
        cur.execute(sql, param)
        result = cur.fetchall()
        cur.close()
        conn.close()
        return result
    
    def login(self, category, user_name, pwd):
        table_dict = {1: "student", 2: "admin"}
        sql = f"SELECT * FROM {table_dict[category]} WHERE user_name=?"
        row = self.fetch_one(sql, (user_name,))  
        
        if row is None:
            messagebox.showerror("错误", "用户不存在")
            return False
        
        if row[1] == pwd:
            messagebox.showinfo("成功", "登录成功")
            self.user_name = user_name
            return True
        else:
            messagebox.showerror("错误", "密码错误")
            return False
    
    def signin(self, category, user_name, pwd):
        if not user_name or not pwd:
            messagebox.showerror("错误", "用户名和密码不能为空")
            return
            
        try:
            table_dict = {1: "student", 2: "admin"}
            sql = f"INSERT INTO {table_dict[category]} (user_name, password) VALUES (?,?)"
            self.execute_sql(sql, (user_name, pwd))
            messagebox.showinfo("成功", "注册成功")
        except:
            messagebox.showerror("错误", "用户名已存在")
        
    def add(self, data):
        sql = "INSERT INTO score (student_name, chinese, math, english) VALUES (?,?,?,?)"
        self.execute_sql(sql, data)

    def modify(self, data):
        sql = "UPDATE score SET chinese=?, math=?, english=? WHERE student_name=?"
        self.execute_sql(sql, data)

    def delete(self, data):
        sql = "DELETE FROM score WHERE student_name=?"
        self.execute_sql(sql, data)
        
    def find(self, data):
        sql = "SELECT * FROM score WHERE student_name=?"
        row = self.fetch_one(sql, data)
        if not row:
            messagebox.showerror("错误", "数据不存在")
            return None
        else:
            return row    

#主窗口
class MainWindow(tk.Frame):
    def __init__(self, container, execute, controller):
        super().__init__(container)
        self.execute = execute
        self.controller = controller
        label_names, rb_names, button_names = ['用户名', '密码'], ['学生', '管理员'], ['注册', '登入']
        
        self.var = tk.IntVar(value=0)
        self.entry_list = []

        # 输入框 + 标签
        for i in range(2):
            tk.Label(self, text=label_names[i], width=10, anchor="w").place(x=350, y=230+i*55)
            entry = tk.Entry(self, width=20)
            entry.place(x=395, y=230+i*55)
            self.entry_list.append(entry)

        # 单选框
        for i in range(2):
            tk.Radiobutton(self, text=rb_names[i], variable=self.var, value=i+1).place(x=350+150*i, y=310)

        # 按钮
        tk.Button(self, text="注册", width=8, command=self.button_signin).place(x=350, y=390)
        tk.Button(self, text="登入", width=8, command=self.button_login).place(x=500, y=390)

        tk.Label(self, text="欢迎来到登入界面", font=("黑体", 24), width=20, anchor="w").place(x=330, y=150)

    def button_signin(self):
        category = self.var.get()
        if category not in (1, 2):
            messagebox.showerror("错误", "请选择身份")
            return
            
        val_user = self.entry_list[0].get()
        password = self.entry_list[1].get()
        self.execute.signin(category, val_user, password)

    def button_login(self):
        category = self.var.get()
        if category not in (1, 2):
            messagebox.showerror("错误", "请选择身份")
            return
            
        val_user = self.entry_list[0].get()
        password = self.entry_list[1].get()
        
        if self.execute.login(category, val_user, password):
            if category == 1:
                self.controller.frame_show(StudentWindow)
            elif category == 2:
                self.controller.frame_show(AdminWindow)

#==================== 【学生界面：修复 + 实现自动填值】 ====================
class StudentWindow(tk.Frame):
    def find(self):
        # 1. 获取姓名
        name = self.entry_list[0].get()
        if not name:
            messagebox.showerror("错误","请输入姓名")
            return

        # 2. 查询（修复字段 + 传参）
        row = self.execute.find((name,))
        
        # 3. 查到了 → 自动填入输入框
        if row is not None:
            for value, entry in zip(row, self.entry_list):
                entry.delete(0, tk.END)
                entry.insert(0, value)

    def __init__(self, container, execute, controller):
        super().__init__(container)
        self.execute = execute
        self.controller = controller
        label_names = ["姓名", "语文", "数学", "英语"]
        self.entry_list = []
        
        self.var = tk.IntVar(value=0)
        
        for i in range(4):
            tk.Label(self, text=label_names[i], width=10, anchor="w").place(x=250+100*i, y=100)
            entry = tk.Entry(self, width=10)
            entry.place(x=250+100*i, y=160)
            self.entry_list.append(entry)

        # 按钮分开，不重叠
        tk.Button(self, text="查询", width=8, command=self.find).place(x=300, y=450)    
        tk.Button(self, text="返回", width=8, command=lambda: controller.frame_show(MainWindow)).place(x=400, y=450)
        
        tk.Label(self, text="欢迎来到学员查询界面", font=("黑体", 24), width=30, anchor="w").place(x=330, y=150)

#==================== 管理员界面 ====================
class AdminWindow(tk.Frame):
    def __init__(self, container, execute, controller):
        super().__init__(container)
        self.execute = execute
        self.controller = controller
        label_names, rb_names = ["姓名", "语文", "数学", "英语"], ["增加", "修改", "删除", "查询"]
        self.var = tk.IntVar(value=0)
        self.entry_list = []
        
        for i in range(4):
            tk.Label(self, text=label_names[i], width=10, anchor="w").place(x=250+100*i, y=100)
            tk.Radiobutton(self, text=rb_names[i], width=10, variable=self.var, value=i+1, anchor="w").place(x=250+100*i, y=250)
            entry = tk.Entry(self, width=10)
            entry.place(x=250+100*i, y=160)
            self.entry_list.append(entry)
            
        tk.Button(self, text="执行", width=8, command=self.do_action).place(x=300, y=450)
        tk.Button(self, text="返回", width=8, command=lambda: controller.frame_show(MainWindow)).place(x=400, y=450)
        tk.Label(self, text="管理员操作界面", font=("黑体", 24), width=30, anchor="w").place(x=330, y=30)

    def do_action(self):
        choice = self.var.get()
        data = [e.get() for e in self.entry_list]
        name = data[0]

        if not name:
            messagebox.showerror("错误","请输入姓名")
            return

        try:
            if choice ==1:
                self.execute.add(data)
                messagebox.showinfo("成功","添加成功")
            elif choice ==2:
                self.execute.modify(data[1:]+[name])
                messagebox.showinfo("成功","修改成功")
            elif choice ==3:
                self.execute.delete((name,))
                messagebox.showinfo("成功","删除成功")
                for e in self.entry_list: e.delete(0,tk.END)
            elif choice ==4:
                row = self.execute.find((name,))
                if row:
                    for v,e in zip(row,self.entry_list):
                        e.delete(0,tk.END)
                        e.insert(0,v)
        except:
            messagebox.showerror("错误","操作失败")
    
if __name__ == "__main__":
    app = App()
    app.mainloop()