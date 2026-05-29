"""门店模块API"""

from api.client import APIClient


class StoreAPI(APIClient):
    """门店相关接口"""

    def get_store_list(self, params=None):
        """获取门店列表"""
        return self.get("/api/v1/stores", params=params)

    def get_store_detail(self, store_id):
        """获取门店详情"""
        return self.get(f"/api/v1/stores/{store_id}")

    def create_store(self, data):
        """创建门店"""
        return self.post("/api/v1/stores", json=data)

    def update_store(self, store_id, data):
        """更新门店信息"""
        return self.put(f"/api/v1/stores/{store_id}", json=data)

    def delete_store(self, store_id):
        """删除门店"""
        return self.delete(f"/api/v1/stores/{store_id}")

    def get_store_stats(self, store_id):
        """获取门店统计"""
        return self.get(f"/api/v1/stores/{store_id}/stats")

    def update_store_status(self, store_id, status):
        """更新门店状态（营业/歇业）"""
        return self.put(f"/api/v1/stores/{store_id}/status", json={
            "status": status
        })

    def get_store_employees(self, store_id, params=None):
        """获取门店员工列表"""
        return self.get(f"/api/v1/stores/{store_id}/employees", params=params)

    def add_employee(self, store_id, data):
        """添加门店员工"""
        return self.post(f"/api/v1/stores/{store_id}/employees", json=data)

    def remove_employee(self, store_id, employee_id):
        """移除门店员工"""
        return self.delete(f"/api/v1/stores/{store_id}/employees/{employee_id}")

    def update_business_hours(self, store_id, hours):
        """更新营业时间"""
        return self.put(f"/api/v1/stores/{store_id}/business-hours", json=hours)

    def get_store_announcements(self, store_id):
        """获取门店公告"""
        return self.get(f"/api/v1/stores/{store_id}/announcements")

    def create_announcement(self, store_id, data):
        """创建门店公告"""
        return self.post(f"/api/v1/stores/{store_id}/announcements", json=data)

    def export_store_data(self, store_id, params=None):
        """导出门店数据"""
        return self.get(f"/api/v1/stores/{store_id}/export", params=params)

    def get_store_permissions(self, store_id):
        """获取门店权限配置"""
        return self.get(f"/api/v1/stores/{store_id}/permissions")

    def update_store_permissions(self, store_id, permissions):
        """更新门店权限配置"""
        return self.put(f"/api/v1/stores/{store_id}/permissions", json=permissions)
