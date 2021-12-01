from mongoengine import *
from copy import deepcopy

# TODO: delete this
'''import datetime

date_time_str = 'Jun 28 2018 7:40AM'
date_time_obj = datetime.datetime.strptime(date_time_str, '%b %d %Y %I:%M%p')

con = connect('test_db_2', host='localhost', port=27017)'''


class Product(Document):
    name = StringField()  # название продукта
    quantity = DecimalField()  # его количество
    unit = StringField()  # единица измерения


class Recipe(Document):  # рецепт
    name = StringField()  # название рецепта
    description = StringField()  # его описание / ссылка на рецепт
    products = ListField(ReferenceField(Product))  # перечень необходимых продуктов и их количество


class Day_plan(Document):  # план по рецептам на день
    date = DateField()  # дата
    day = StringField()  # день недели
    recipes = ListField(ReferenceField(Recipe))  # перечень рецептов


class User(Document):  # общая информация о пользователе
    user_id = LongField()  # уникальный id пользователя
    full_plan = ListField(ReferenceField(Day_plan))  # план на неделю
    availible_products = ListField(ReferenceField(Product))  # какие продукты есть
    separate_products = ListField(ReferenceField(Product))  # какие продукты купить


# создание нового пользователя при его первичном обращении к боту
def make_new_user(u_id):
    if len(User.objects(user_id=u_id)) != 0:  # проверка, существует ли уже пользователь
        return
    user_new = User(user_id=u_id, full_plan=[], availible_products=[])
    user_new.save()


#  ------ блок с функциями удаления ------

# очистить информацию о пользователе (всю, кроме id)
def delete_all_user_info(u_id):
    delete_user_plan(u_id)
    delete_user_av_products(u_id)
    delete_user_sep_products(u_id)


# очистить план на неделю (или другой промежуток времени) полностью
def delete_user_plan(u_id):
    u = User.objects.get(user_id=u_id)
    for day in u.full_plan:
        delete_single_day(u_id, day.date)
    u.modify(full_plan=[])


# очистить список продуктов в наличии полностью
def delete_user_av_products(u_id):
    u = User.objects.get(user_id=u_id)
    for prod in u.availible_products:
        prod.delete()
    User.objects(user_id=u_id).modify(availible_products=[])


#  очистить список независимых продуктов из корзины полностью
def delete_user_sep_products(u_id):
    u = User.objects.get(user_id=u_id)
    for prod in u.separate_products:
        prod.delete()
    User.objects(user_id=u_id).modify(separate_products=[])


#  удалить информацию о конкретном дне
def delete_single_day(u_id, single_day_date):
    u = User.objects.get(user_id=u_id)
    u_fp = u.full_plan
    for day_for_del in u_fp:
        if day_for_del.date == single_day_date:
            del_day = day_for_del
            break
        print("cant found date")
        return
    for rec in del_day.recipes:
        delete_recipe(u_id, single_day_date, rec.name)
    u_fp.remove(del_day)
    u.modify(full_plan=u_fp)
    del_day.delete()


# удалить информацию о конкретном рецепте
def delete_recipe(u_id, day_date, recipe_name):
    u_fp = User.objects.get(user_id=u_id).full_plan
    for day_for_del in u_fp:
        if day_for_del.date == day_date:
            del_day = day_for_del
            break
        print("cant found day")
        return
    for rec in del_day.recipes:
        if rec.name == recipe_name:
            rec_del = rec
            new_rec = del_day.recipes
            new_rec.remove(rec)
            del_day.modify(recipes=new_rec)
            break
        print("cant found recipe")
        return
    for prod in rec_del.products:
        prod.delete()
    rec_del.delete()


#  удалить независимый продукт из корзины
def delete_sep_product(u_id, product_name):
    u = User.objects.get(user_id=u_id)
    for prod in u.separate_products:
        if prod.name == product_name:
            del_prod = prod
            print(del_prod)
            break
        print("no such separate product")
        return
    u_sep = u.separate_products
    u_sep.remove(del_prod)
    u.modify(separate_products=u_sep)
    del_prod.delete()


#  ----- блок с функциями добавления -----
def make_product(product_name, product_quantity, product_unit):
    new_product = Product(name=product_name, quantity=product_quantity, unit=product_unit)
    new_product.save()
    return new_product


def add_to_available_products(u_id, p_name, p_qua, p_unit):
    u = User.objects.get(user_id=u_id)
    modify_prod = is_in_available_products(u, p_name)
    if modify_prod:
        if modify_prod.unit != p_unit:
            #  TODO: перевод единиц измерения
            pass
        else:  # если уже есть такой продукт в корзине и все ок с ед.измерения -- увеличиваем кол-во
            modify_prod.modify(inc__quantity=p_qua)
            return
    new_product = Product(name=p_name, quantity=p_qua, unit=p_unit)  # если нет в корзине -- добавляем в корзину
    new_product.save()
    u.modify(push__availible_products=new_product)


def add_to_separate_products(u_id, p_name, p_qua, p_unit):
    u = User.objects.get(user_id=u_id)
    modify_prod = is_in_separate_products(u, p_name)
    if modify_prod:
        if modify_prod.unit != p_unit:
            #  TODO: перевод единиц измерения
            pass
        else:  # если уже есть такой продукт в корзине и все ок с ед.измерения -- увеличиваем кол-во
            modify_prod.modify(inc__quantity=p_qua)
            return
    new_product = Product(name=p_name, quantity=p_qua, unit=p_unit)  # если нет в корзине -- добавляем в корзину
    new_product.save()
    u.modify(push__separate_products=new_product)


def add_new_day(u_id, day_date, day='Monday', *recipes):
    u = User.objects.get(user_id=u_id)
    new_day = is_exist_day(u, day_date)
    if new_day == False:
        new_day = Day_plan(date=day_date, day=day, recipes=recipes)
        new_day.save()
        u.modify(push__full_plan=new_day)
    else:
        day_info = Day_plan.objects.filter(date=day_date, day=new_day.day, recipes=new_day.recipes)[0]
        u_fp = u.full_plan
        u_fp.remove(new_day)
        u.modify(full_plan=u_fp)
        day_info.modify(push__recipes=recipes[0])
        u.modify(push__full_plan=day_info)


def make_new_recipe(recipe_name, recipe_description='', *products):
    if isinstance(products[0], list):
        new_recipe = Recipe(name=recipe_name, description=recipe_description, products=products[0])
    else:
        new_recipe = Recipe(name=recipe_name, description=recipe_description, products=products)
    new_recipe.save()
    return new_recipe


# в работе
def add_recipe_to_day(u_id, day_date, recipe, *day):
    add_new_day(u_id, day_date, day, recipe)


# ----- блок с функциями проверки "is in" ------

def is_in_available_products(user, product_name):
    for av_p in user.availible_products:
        if av_p.name == product_name:
            return av_p
    return False


def is_in_separate_products(user, product_name):
    for av_p in user.separate_products:
        if av_p.name == product_name:
            return av_p
    return False


def is_exist_day(user, day_date):
    for day in user.full_plan:
        if day.date == day_date:
            return day
    return False


def is_recipe_in_day(user, day_date, recipe_name):
    check_day = 0
    for day in user.full_plan:
        if day.date == day_date:
            check_day = day
            break
    if check_day == 0:
        return False
    for recipe in check_day.recipes:
        if recipe.name == recipe_name:
            return True
    return False


# ---- get функции ----


def get_day(user, day_date):
    for day in user.full_plan:
        if day.date == day_date:
            return day
    return 0


# функция вспомогательная, для отладки
def print_all_user_info(u_id):
    u = User.objects.get(user_id=u_id)
    res_str = "User id: " + str(u.user_id) + "; user_plan:"
    for rec in u.full_plan:
        res_str += f' date -{rec.date},'
        res_str += f'rec_count={len(rec.recipes)},'
        res_str += f'rec={rec.recipes}'
    res_str += '; availible products:'
    for a_pr in u.availible_products:
        res_str += f'product - {a_pr.name},cou = {a_pr.quantity}'
    res_str += '; sep products:'
    for s_pr in u.separate_products:
        res_str += f'sep product - {s_pr.name}, cou = {s_pr.quantity}
    print(res_str)


'''User.objects(user_id=16).delete()
tom = Product(name='tomato', quantity=3, unit='kg')
tom.save()
milk = Product(name='milk', quantity=1, unit='l')
milk.save()
tom1 = Product(name='tomato', quantity=3, unit='kg')
tom1.save()
milk1 = Product(name='milk', quantity=1, unit='l')
milk1.save()'''
'''
tom2 = Product(name='tomato', quantity=3, unit='kg')
tom2.save()
milk2 = Product(name='milk', quantity=1, unit='l')
milk2.save()
recipe_1 = Recipe(name='salat', description='very tasty', products=[tom])
recipe_1.save()
recipe_2 = Recipe(name='milk', description='for me', products = [milk])
recipe_2.save()
recipe_3 = Recipe(name='salat', description='very tasty', products=[tom2])
recipe_3.save()
recipe_4 = Recipe(name='milk', description='for me', products=[milk2])
recipe_4.save()
first_day = Day_plan(date=date_time_obj.date(), day='Monday', recipes=[recipe_1, recipe_2])
first_day.save()
second_day = Day_plan(date=date_time_obj.date()+datetime.timedelta(days=1), day='Monday', recipes=[recipe_3, recipe_4])
second_day.save()'''

'''new_user = User(user_id=16, full_plan=[], availible_products=[tom, milk], separate_products=[tom1, milk1])
new_user.save()

print_all_user_info(16)
tom2 = Product(name='tomato', quantity=3, unit='kg')
tom2.save()
prod1 = make_product('bread', 1, 'kg')
prod2 = make_product('sugar', 0.6, 'kg')
prod3 = make_product('sugar', 0.6, 'kg')
add_new_day(16, datetime.date.today())
recipe1 = make_new_recipe('buter', 'vkusno', [prod1, prod2])
recipe2 = make_new_recipe('bu-buter', 'vkusno-o-o', [prod3, tom2])
add_recipe_to_day(16, datetime.date.today(), recipe1)
add_recipe_to_day(16, datetime.date.today(), recipe2)

print_all_user_info(16)

delete_all_user_info(16)

print_all_user_info(16)'''
