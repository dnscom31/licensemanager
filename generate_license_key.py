# generate_license_key.py

import requests
import tkinter as tk
from tkinter import messagebox, ttk
import os

# 서버 URL 설정 (프로토콜 포함)
SERVER_URL = 'https://licensemanager-production.up.railway.app'

# 관리자 토큰 (환경 변수에서 가져옴)
ADMIN_TOKEN = os.environ.get("ADMIN_TOKEN", "6730bb41-cbb8-8004-b318-bf27d48d445f")

# 로그인 정보
CREDENTIALS = {
    'manager': 'manager1',
    'master': 'master1'
}

class LoginWindow:
    def __init__(self, root, on_login):
        self.root = root
        self.on_login = on_login
        self.root.title("Login")
        self.root.geometry("300x150")
        self.create_widgets()

    def create_widgets(self):
        frame = tk.Frame(self.root)
        frame.pack(padx=20, pady=20)

        label_id = tk.Label(frame, text="ID:")
        label_id.grid(row=0, column=0, pady=5, sticky='e')
        self.entry_id = tk.Entry(frame)
        self.entry_id.grid(row=0, column=1, pady=5)

        label_password = tk.Label(frame, text="Password:")
        label_password.grid(row=1, column=0, pady=5, sticky='e')
        self.entry_password = tk.Entry(frame, show="*")
        self.entry_password.grid(row=1, column=1, pady=5)

        button_login = tk.Button(frame, text="Login", command=self.validate_login)
        button_login.grid(row=2, column=0, columnspan=2, pady=10)

    def validate_login(self):
        user_id = self.entry_id.get()
        password = self.entry_password.get()

        if user_id in CREDENTIALS and CREDENTIALS[user_id] == password:
            role = user_id  # 'manager' or 'master'
            self.on_login(role)
        else:
            messagebox.showerror("Login Failed", "Invalid ID or Password")

class MainWindow:
    def __init__(self, root, role):
        self.root = root
        self.role = role  # 'manager' or 'master'
        self.root.title("License Manager - " + self.role.capitalize())
        self.create_widgets()
        self.update_license_list()

    def generate_license_key(self, user_id):
        try:
            response = requests.post(f"{SERVER_URL}/generate_license", json={'user_id': user_id})
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 'generated':
                return data.get('license_key')
            else:
                messagebox.showerror("Error", "Failed to generate license key.")
                return None
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"An error occurred while generating the license: {e}")
            return None

    def register_license(self, user_id, license_key):
        # 이제 서버에서 이미 라이선스를 생성하고 등록하므로 이 함수는 필요하지 않을 수 있습니다.
        # 하지만 여전히 라이선스 등록이 별도로 필요한 경우 유지할 수 있습니다.
        try:
            response = requests.post(f"{SERVER_URL}/register_license", json={
                'user_id': user_id,
                'license_key': license_key
            })
            if response.status_code == 200 and response.json().get('status') == 'registered':
                return True
            else:
                return False
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while registering the license: {e}")
            return False

    def invalidate_license(self, license_key):
        try:
            response = requests.post(f"{SERVER_URL}/invalidate_license", json={
                'license_key': license_key,
                'admin_token': ADMIN_TOKEN
            })
            if response.status_code == 200 and response.json().get('status') == 'invalidated':
                return True
            else:
                messagebox.showerror("Error", f"Failed to invalidate license key: {response.json().get('detail')}")
                return False
        except Exception as e:
            messagebox.showerror("Error", f"An error occurred while invalidating the license: {e}")
            return False

    def fetch_licenses(self):
        try:
            response = requests.get(f"{SERVER_URL}/get_licenses")
            response.raise_for_status()
            data = response.json()
            if data.get('status') == 'success':
                return data.get('licenses', [])
            else:
                messagebox.showerror("Error", f"Failed to fetch licenses: {data.get('detail')}")
                return []
        except requests.exceptions.RequestException as e:
            messagebox.showerror("Error", f"An error occurred while fetching licenses: {e}")
            return []
        except ValueError as e:
            messagebox.showerror("Error", f"Invalid JSON response: {e}")
            return []

    def on_generate(self):
        user_id = self.entry_user_id.get()
        if not user_id:
            messagebox.showwarning("Input Error", "Please enter a User ID.")
            return

        # 역할에 따른 처리
        if self.role == 'manager':
            # Manager는 자신이 생성한 라이선스만 관리
            # User ID 앞에 'manager_'를 추가하여 식별
            user_id = f"manager_{user_id}"
            # 현재 유효한 라이선스 개수 확인
            licenses = self.fetch_licenses()
            valid_licenses = [license for license in licenses if license['is_valid'] and license['user_id'].startswith('manager_')]
            if len(valid_licenses) >= 100:
                messagebox.showerror("Error", "Maximum number of valid licenses (100) reached.")
                return

        license_key = self.generate_license_key(user_id)
        if license_key:
            messagebox.showinfo("Success", f"License key for user {user_id} is:\n{license_key}")
            # 라이선스 목록 갱신
            self.update_license_list()
        else:
            messagebox.showerror("Error", "Failed to generate license key.")

    def on_delete(self):
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showwarning("Selection Error", "Please select a license to delete.")
            return

        license_key = self.tree.item(selected_item)['values'][2]  # 라이선스 키는 세 번째 열
        confirm = messagebox.askyesno("Confirm Delete", "Are you sure you want to delete the selected license?")
        if confirm:
            if self.invalidate_license(license_key):
                messagebox.showinfo("Success", "License key has been invalidated.")
                # 라이선스 목록 갱신
                self.update_license_list()
                # 선택된 라이선스 키 초기화
                self.entry_license_key.delete(0, tk.END)
            else:
                messagebox.showerror("Error", "Failed to invalidate license key.")

    def update_license_list(self):
        # 기존 항목 모두 삭제
        for item in self.tree.get_children():
            self.tree.delete(item)
        # 라이선스 목록 가져오기
        licenses = self.fetch_licenses()
        # 역할에 따른 필터링
        if self.role == 'manager':
            # Manager는 자신이 생성한 라이선스만 필터링
            licenses = [license for license in licenses if license['is_valid'] and license['user_id'].startswith('manager_')]
        else:
            # Master는 모든 유효한 라이선스를 표시
            licenses = [license for license in licenses if license['is_valid']]
        # 트리에 항목 추가
        for idx, license in enumerate(licenses, start=1):
            self.tree.insert('', 'end', values=(idx, license['user_id'], license['license_key']))

    def on_tree_select(self, event):
        selected_item = self.tree.selection()
        if selected_item:
            license_key = self.tree.item(selected_item)['values'][2]
            # 라이선스 키를 Entry 위젯에 표시
            self.entry_license_key.config(state='normal')
            self.entry_license_key.delete(0, tk.END)
            self.entry_license_key.insert(0, license_key)
            self.entry_license_key.config(state='readonly')

    def create_widgets(self):
        # 프레임 구성: 좌측에 라이선스 생성, 우측에 라이선스 목록
        frame_left = tk.Frame(self.root)
        frame_left.pack(side='left', fill='both', expand=True, padx=10, pady=10)

        frame_right = tk.Frame(self.root)
        frame_right.pack(side='right', fill='both', expand=True, padx=10, pady=10)

        # 좌측: 라이선스 생성
        label_user_id = tk.Label(frame_left, text="User ID:")
        label_user_id.pack(padx=5, pady=5)
        self.entry_user_id = tk.Entry(frame_left, width=30)
        self.entry_user_id.pack(padx=5, pady=5)

        button_generate = tk.Button(frame_left, text="Generate License", command=self.on_generate)
        button_generate.pack(padx=5, pady=5)

        # 우측: 라이선스 목록 및 삭제
        label_license_list = tk.Label(frame_right, text="License List:")
        label_license_list.pack(padx=5, pady=5)

        columns = ('number', 'user_id', 'license_key')
        self.tree = ttk.Treeview(frame_right, columns=columns, show='headings')
        self.tree.heading('number', text='Number')
        self.tree.heading('user_id', text='User ID')
        self.tree.heading('license_key', text='License Key')

        # 열 너비 조정
        self.tree.column('number', width=50, anchor='center')
        self.tree.column('user_id', width=150, anchor='center')
        self.tree.column('license_key', width=400)

        self.tree.pack(padx=5, pady=5, fill='both', expand=True)

        # 라이선스 키 표시 및 복사 기능 추가
        label_selected_key = tk.Label(frame_right, text="Selected License Key:")
        label_selected_key.pack(padx=5, pady=5)

        self.entry_license_key = tk.Entry(frame_right, width=50, state='readonly')
        self.entry_license_key.pack(padx=5, pady=5)

        button_delete = tk.Button(frame_right, text="Delete Selected License", command=self.on_delete)
        button_delete.pack(padx=5, pady=5)

        # Treeview에서 항목 선택 시 이벤트 바인딩
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)

def main():
    root = tk.Tk()
    root.withdraw()  # 로그인 창이 닫힌 후 메인 창이 나타나도록 숨김

    def open_main_window(role):
        login_window.root.destroy()
        main_window = tk.Toplevel(root)
        MainWindow(main_window, role)

    login_window = LoginWindow(tk.Toplevel(root), open_main_window)
    root.mainloop()

if __name__ == "__main__":
    main()
