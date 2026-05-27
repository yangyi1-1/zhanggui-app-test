"""商品模块API"""

from api.client import APIClient


class ProductAPI(APIClient):
    """商品相关接口"""

    def get_category_list(self, store_id):
        """获取商品分类列表"""
        return self.get("/api/v1/categories", params={"storeId": store_id})

    def create_category(self, data):
        """创建商品分类"""
        return self.post("/api/v1/categories", json=data)

    def update_category(self, category_id, data):
        """更新商品分类"""
        return self.put(f"/api/v1/categories/{category_id}", json=data)

    def delete_category(self, category_id):
        """删除商品分类"""
        return self.delete(f"/api/v1/categories/{category_id}")

    def get_product_list(self, params=None):
        """获取商品列表"""
        return self.get("/api/v1/products", params=params)

    def get_product_detail(self, product_id):
        """获取商品详情"""
        return self.get(f"/api/v1/products/{product_id}")

    def create_product(self, data):
        """创建商品"""
        return self.post("/api/v1/products", json=data)

    def update_product(self, product_id, data):
        """更新商品"""
        return self.put(f"/api/v1/products/{product_id}", json=data)

    def delete_product(self, product_id):
        """删除商品"""
        return self.delete(f"/api/v1/products/{product_id}")

    def update_product_status(self, product_id, status):
        """更新商品状态（上架/下架）"""
        return self.put(f"/api/v1/products/{product_id}/status", json={
            "status": status
        })

    def batch_update_products(self, product_ids, action):
        """批量操作商品"""
        return self.post("/api/v1/products/batch", json={
            "productIds": product_ids,
            "action": action,
        })
