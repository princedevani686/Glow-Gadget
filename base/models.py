from django.db import models


class AreaVO(models.Model):
    area_id = models.AutoField(db_column="area_id", primary_key=True,
                               null=False)
    area_name = models.CharField(db_column="area_name", max_length=255,
                                 default="", null=False)
    area_code = models.IntegerField(db_column="area_code", null=False)

    def __str__(self):
        return '{} {}'.format(self.area_name, self.area_code)

    def __as_dict__(self):
        return {
            "area_name": self.area_name,
            "area_code": self.area_code
        }

    class Meta:
        db_table = "area_table"


class CategoryVO(models.Model):
    category_id = models.AutoField(db_column="category_id", primary_key=True,
                                   null=False)
    category_image = models.ImageField(db_column="category_image",
                                       upload_to='static/adminResources/categoryImage/',
                                       null=True, blank=True)
    category_name = models.CharField(db_column="category_name", max_length=255,
                                     default="", null=False)
    category_description = models.TextField(db_column="category_description",
                                            max_length=255, default="",
                                            null=False)

    def __str__(self):
        return '{} {} {}'.format(self.category_image, self.category_name,
                                 self.category_description)

    def __as_dict__(self):
        return {
            "category_id": self.category_id,
            "category_image": self.category_image,
            "category_name": self.category_name,
            "category_description": self.category_description
        }

    class Meta:
        db_table = "category_table"


class SubCategoryVO(models.Model):
    subcategory_id = models.AutoField(db_column="subcategory_id",
                                      primary_key=True, null=False)
    subcategory_image = models.ImageField(db_column="subcategory_image",
                                          upload_to='static/adminResources/subcategoryImage/',
                                          null=True, blank=True)
    subcategory_name = models.CharField(db_column="subcategory_name",
                                        max_length=255, default="", null=False)
    subcategory_description = models.TextField(
        db_column="subcategory_description", max_length=255, default="",
        null=False)
    subcategory_category_vo = models.ForeignKey(CategoryVO,
                                                on_delete=models.CASCADE,
                                                db_column='subcategory_category_id')

    def __str__(self):
        return '{} {} {}'.format(self.subcategory_image, self.subcategory_name,
                                 self.subcategory_description)

    def __as_dict__(self):
        return {
            "subcategory_id": self.subcategory_id,
            "subcategory_image": self.subcategory_image,
            "subcategory_name": self.subcategory_name,
            "subcategory_description": self.subcategory_description,
            "subcategory_category_vo": self.subcategory_category_vo
        }

    class Meta:
        db_table = "subcategory_table"


class ProductVO(models.Model):
    product_id = models.AutoField(db_column="product_id", primary_key=True,
                                  null=False)
    product_name = models.CharField(db_column="product_name", max_length=50,
                                    default="", null=False)
    product_description = models.TextField(db_column="product_description",
                                           max_length=500, default="",
                                           null=False)
    product_quantity = models.IntegerField(db_column="product_quantity",
                                           null=False)
    product_price = models.IntegerField(db_column="product_price", null=False)
    product_color = models.CharField(db_column="product_color", max_length=100,
                                     default="", null=False)
    product_adjustable = models.CharField(db_column="product_adjustable",
                                             default="",max_length=100,
                                             null=False)
    product_material = models.CharField(db_column="product_material",
                                        max_length=100,
                                        default="", null=False)
    product_image = models.ImageField(db_column="product_image",
                                      upload_to='static/adminResources/product/')
    product_category_id = models.ForeignKey(CategoryVO,
                                            db_column="product_category_id",
                                            on_delete=models.CASCADE)
    product_subcategory_id = models.ForeignKey(SubCategoryVO,
                                               db_column="product_subcategory_id",
                                               on_delete=models.CASCADE)

    def __str__(self):
        return '{} {} {} {} {} {} {} {}'.format(self.product_name,
                                                self.product_description,
                                                self.product_quantity,
                                                self.product_price,
                                                self.product_color,
                                                self.product_adjustable,
                                                self.product_material,
                                                self.product_image)

    def __as_dict__(self):
        return {
            "product_id": self.product_id,
            "product_name": self.product_name,
            "product_description": self.product_description,
            "product_quantity": self.product_quantity,
            "product_price": self.product_price,
            "product_color": self.product_color,
            "product_adjustable": self.product_adjustable,
            "product_material": self.product_material,
            "product_image": self.product_image,
            "product_category_id": self.product_category_id,
            "product_subcategory_id": self.product_subcategory_id,
        }

    class Meta:
        db_table = "product_table"


class LoginVO(models.Model):
    login_id = models.AutoField(db_column="login_id", primary_key=True,
                                null=False)
    login_username = models.CharField(db_column="login_username",
                                      max_length=200, default="", null=False)
    login_password = models.CharField(db_column="login_password",
                                      max_length=200, default="", null=False)
    login_role = models.CharField(db_column="login_role", max_length=10,
                                  default="", null=False)
    login_status = models.BooleanField(db_column="login_status", max_length=1,
                                       default="", null=False)

    def __str__(self):
        return '{} {} {}'.format(self.login_username,
                                 self.login_password,
                                 self.login_role, )

    def __as_dict__(self):
        return {
            "login_id": self.login_id,
            "login_username": self.login_username,
            "login_password": self.login_password,
            "login_role": self.login_role,
            "login_status": self.login_status
        }

    class Meta:
        db_table = "login_table"


class UserVO(models.Model):
    user_id = models.AutoField(db_column="user_id", primary_key=True,
                               null=False)
    user_firstname = models.CharField(db_column="user_firstname",
                                      max_length=200, default="", null=False)
    user_lastname = models.CharField(db_column="user_lastname", max_length=200,
                                     default="", null=False)
    user_gender = models.CharField(db_column="user_gender", max_length=10,
                                   default="", null=False)
    user_address = models.CharField(db_column="user_address", max_length=200, default="", null=False)
    user_login_vo = models.ForeignKey(LoginVO, on_delete=models.CASCADE,
                                      db_column="user_login_id")
    user_area_vo = models.ForeignKey(AreaVO, on_delete=models.CASCADE,
                                     db_column="user_area_id")

    def __str__(self):
        return '{} {} {} {}'.format(self.user_firstname,
                                 self.user_lastname,
                                 self.user_gender,
                                    self.user_address,
                                 )

    def __as_dict__(self):
        return {
            "user_id": self.user_id,
            "user_firstname": self.user_firstname,
            "user_lastname": self.user_lastname,
            "user_gender": self.user_gender,
            "user_address": self.user_address,
            "user_login_vo": self.user_login_vo,
            "user_area_vo": self.user_area_vo
        }

    class Meta:
        db_table = "register_table"

class CartVO(models.Model):
    cart_id = models.AutoField(db_column="cart_id", primary_key=True,
                                   null=False)
    cart_quantity = models.IntegerField(db_column="cart_quantity", default="",
                                        null=False)
    cart_subtotal = models.IntegerField(db_column="cart_subtotal", default="",
                                        null=False)
    cart_user_vo = models.ForeignKey(UserVO,db_column="cart_user_id",
                                     on_delete=models.CASCADE,null=False)
    cart_product_vo = models.ForeignKey(ProductVO,db_column="cart_product_id",
                                        on_delete=models.CASCADE,null=False)

    def __str__(self):
        return '{} {}'.format(self.cart_quantity,
                              self.cart_subtotal)
    def __as_dict__(self):
        return {
            "cart_id": self.cart_id,
            "cart_quantity": self.cart_quantity,
            "cart_subtotal": self.cart_subtotal,
            "cart_user_vo": self.cart_user_vo,
            "cart_product_vo": self.cart_product_vo
        }

    class Meta:
        db_table = 'cart_table'

class OrderVO(models.Model):
    order_id = models.AutoField(db_column="order_id",primary_key=True,
                                   null=False)
    order_date = models.DateField(db_column="order_date",null=False)
    order_delivery_date = models.DateField(db_column="order_delivery_date",
                                           null=False)
    order_status = models.CharField(db_column="order_status",max_length=255,
                                    null=True, default="")
    order_quantity = models.IntegerField(db_column="order_quantity", default="",
                                        null=False)
    order_total = models.IntegerField(db_column="order_total", default="",
                                        null=False)
    order_invoice = models.IntegerField(db_column="order_invoice", null=False
                                        , default="")
    order_product_vo = models.ForeignKey(ProductVO,
                                         db_column="order_product_id",
                                         on_delete=models.CASCADE,null=False,
                                         default="")
    order_user_vo = models.ForeignKey(UserVO,db_column="order_user_id",
                                      on_delete=models.CASCADE,null=False,
                                      default="")

    def __str__(self):
        return '{} {} {} {} {}'.format(self.order_date,
                                    self.order_delivery_date,
                                    self.order_status,
                                    self.order_quantity,
                                    self.order_total
                                    )
    def __as_dict__(self):
        return {
            'order_id': self.order_id,
            'order_date': self.order_date,
            'order_delivery_date': self.order_delivery_date,
            'order_status': self.order_status,
            'order_product_vo': self.order_product_vo,
            'order_user_vo': self.order_user_vo
        }

    class Meta:
        db_table = 'order_table'

class ComplainVO(models.Model):
    complain_id = models.AutoField(db_column="complain_id", primary_key=True,
                                   null=False)
    complain_subject = models.CharField(db_column="complain_subject",
                                        max_length=255, default="", null=False)
    complain_description = models.TextField(db_column="complain_description",
                                            max_length=500, default="",
                                            null=False)
    complain_date = models.DateField(db_column="complain_date",
                                     null=False)
    complain_status = models.CharField(db_column="complain_status",
                                       max_length=255, default="", null=False)
    complain_user_vo = models.ForeignKey(UserVO,
                                         db_column="complain_user_id",
                                         on_delete=models.CASCADE,
                                         null=False, default="")

    def __str__(self):
        return '{} {} {} {}'.format(self.complain_subject,
                                    self.complain_description,
                                    self.complain_date,
                                    self.complain_status)

    def __as_dict__(self):
        return {
            "complain_id": self.complain_id,
            "complain_subject": self.complain_subject,
            "complain_description": self.complain_description,
            "complain_date": self.complain_date,
            "complain_status": self.complain_status,
            "complain_user_vo": self.complain_user_vo
        }

    class Meta:
        db_table = "complain_table"


class ReplyVO(models.Model):
    reply_id = models.AutoField("reply_id", primary_key=True, null=False)
    reply_description = models.TextField("reply_description", max_length=500,
                                         default="", null=False)
    reply_datetime = models.DateTimeField(db_column="reply_datetime",
                                          null=False,
                                          default="")
    reply_complain_vo = models.ForeignKey(ComplainVO,
                                          db_column="reply_complain_id",
                                          on_delete=models.CASCADE,
                                          null=False)
    reply_login_vo = models.ForeignKey(LoginVO, db_column="reply_login_id",
                                       on_delete=models.CASCADE, null=False)

    def __str__(self):
        return '{} {}'.format(self.reply_description,
                              self.reply_datetime)

    def as_dict(self):
        return {
            "reply_id": self.reply_id,
            "reply_description": self.reply_description,
            "reply_date": self.reply_datetime,
            "reply_complain_vo": self.reply_complain_vo,
            "reply_login_vo": self.reply_login_vo
        }

    class Meta:
        db_table = "reply_table"


class DeviceInfoVO(models.Model):
    device_id = models.AutoField(db_column="device_id", primary_key=True,
                                 null=False)

    device_identity = models.TextField(db_column="device_identity",
                                       max_length=500, default="",
                                       null=False)

    device_login_vo = models.ForeignKey(LoginVO,
                                        db_column="device_login_id",
                                        on_delete=models.CASCADE, null=False)

    class Meta:
        db_table = "device_info_table"

