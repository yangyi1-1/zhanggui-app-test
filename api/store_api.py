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
