from mongoengine import *


# подключение к базе, по default указать имя и адрес нашей базы, где все вертится
def connect_to_base(base_name='test_db_4', base_host='localhost', base_port=27017):
    con = connect(base_name, host=base_host, port=base_port)


class Product(Document):
    name = StringField()  # название продукта
    quantity = DecimalField()  # его количество
    unit = StringField()  # единица измерения
    has_null_parts = BooleanField()  # сохраняем, встречались ли нам "нулевые" единицы измерения


class Recipe(Document):  # рецепт
    name = StringField()  # название рецепта
    description = StringField()  # его описание / ссылка на рецепт
    portion_count = DecimalField()
    products = ListField(ReferenceField(Product))  # перечень необходимых продуктов и их количество


class Day_plan(Document):  # план по рецептам на день
    date = StringField()  # дата
    day = StringField()  # день недели
    recipes = ListField(ReferenceField(Recipe))  # перечень рецептов


class User(Document):  # общая информация о пользователе
    user_id = LongField()  # уникальный id пользователя
    full_plan = ListField(ReferenceField(Day_plan))  # план на неделю
    available_products = ListField(ReferenceField(Product))  # какие продукты есть
    separate_products = ListField(ReferenceField(Product))  # какие продукты купить
    state = IntField()  # вспомогательное поле
    n_days = IntField()  # количество дней, для которых составлен роцион пользователя
    day = IntField()  # текущий день


# создание нового пользователя при его первичном обращении к боту
def make_new_user(u_id):
    if len(User.objects(user_id=u_id)) != 0:  # проверка, существует ли уже пользователь
        return
    user_new = User(user_id=u_id, full_plan=[], available_products=[], state=1, n_days=0, day=0)
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
    for prod in u.available_products:
        prod.delete()
    User.objects(user_id=u_id).modify(available_products=[])


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


#  удалить/уменьшить наличие продукта из списка независимых продуктов в корзине
def delete_sep_product(u_id, product_name, delete_product=True, dec_value=0, dec_unit=''):
    u = User.objects.get(user_id=u_id)
    for prod in u.separate_products:
        if prod.name == product_name:
            del_prod = prod
            break
        print("no such separate product")
        return
    u_sep = u.separate_products
    if delete_product:
        u_sep.remove(del_prod)
        u.modify(separate_products=u_sep)
        del_prod.delete()
    else:
        add_to_separate_products(u_id, product_name, -dec_value, dec_unit)


#  удалить/ уменьшить наличие продукт из списка в "холодильнике"
def delete_available_product(u_id, product_name, delete_product=True, dec_value=0, dec_unit=''):
    u = User.objects.get(user_id=u_id)
    for prod in u.savailable_products:
        if prod.name == product_name:
            del_prod = prod
            break
        print("no such separate product")
        return
    u_sep = u.available_products
    if delete_product:
        u_sep.remove(del_prod)
        u.modify(available_products=u_sep)
        del_prod.delete()
    else:
        add_to_available_products(u_id, product_name, -dec_value, dec_unit)


#  ----- блок с функциями добавления -----

# создание продукта (вспомогательная функция для создания рецепта)
def make_product(product_name, product_quantity, product_unit):
    is_none = False
    if product_unit == 'none':
        is_none = True
    new_product = Product(name=product_name, quantity=product_quantity, unit=product_unit, has_null_parts=is_none)
    new_product.save()
    return new_product


# пополнить список продуктов, которые уже есть у пользователя
def add_to_available_products(u_id, p_name, p_qua, p_unit):
    u = User.objects.get(user_id=u_id)
    modify_prod = is_in_available_products(u, p_name)
    if modify_prod:
        if modify_prod.unit != p_unit:
            if modify_prod.has_null_parts and modify_prod.unit == 'None':
                modify_prod.modify(quantity=p_qua, unit=p_unit)
                return
            if not modify_prod.has_null_parts and p_unit == 'none':
                modify_prod.modify(has_null_parts=True)
            print("O-o-ops, закралась другая единица измерения")
        else:
            # если уже есть такой продукт в корзине и все ок с ед.измерения -- увеличиваем кол-во
            if modify_prod.quantity + p_qua <= 0:
                delete_available_product(u_id, p_name)
                return
            modify_prod.modify(inc__quantity=p_qua)
            return
    new_product = make_product(p_name, p_qua, p_unit)  # если нет в корзине -- добавляем в корзину
    new_product.save()
    u.modify(push__available_products=new_product)


# пополнить список продуктов, которые нужно купить просто так
def add_to_separate_products(u_id, p_name, p_qua, p_unit):
    u = User.objects.get(user_id=u_id)
    modify_prod = is_in_separate_products(u, p_name)
    if modify_prod:
        if modify_prod.unit != p_unit:
            if modify_prod.has_null_parts and modify_prod.unit == 'none':
                modify_prod.modify(quantity=p_qua, unit=p_unit)
                return
            if not modify_prod.has_null_parts and p_unit == 'none':
                modify_prod.modify(has_null_parts=True)
            print("O-o-ops, закралась другая единица измерения")
        else:  # если уже есть такой продукт в корзине и все ок с ед.измерения -- увеличиваем кол-во
            if modify_prod.quantity + p_qua <= 0:
                delete_sep_product(u_id, p_name)
                return
            modify_prod.modify(inc__quantity=p_qua)
            return
    if p_qua < 0:
        print("Alert: пользователь ввел отрицательное количество продукта")
        return
    new_product = make_product(p_name, p_qua, p_unit)  # если нет в корзине -- добавляем в корзину
    new_product.save()
    u.modify(push__separate_products=new_product)


# добавляем новый день/ обновляем информацию о нем
def add_new_day(u_id, day_date, day, *recipes):
    u = User.objects.get(user_id=u_id)
    new_day = is_exist_day(u, day_date)
    if not new_day:
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


# создание нового рецепта (вспомогательная функция, нужна для добавления рецепта в конкретный день)
def make_new_recipe(recipe_name, recipe_description='', recipe_count=1,  *products):
    if isinstance(products[0], list):
        new_recipe = Recipe(name=recipe_name, description=recipe_description, portion_count=recipe_count, products=products[0])
    else:
        new_recipe = Recipe(name=recipe_name, description=recipe_description, portion_count=recipe_count, products=products)
    new_recipe.save()
    return new_recipe


# добавление нового рецепта в план
def add_recipe_to_day(u_id, day_date, recipe, *day):
    add_new_day(u_id, day_date, day, recipe)


# изменение количество дней, для которых пишем рацион
def set_user_n_days(u_id, n_days):
    u = User.objects.get(user_id=u_id)
    u.modify(n_days=n_days)


# изменение статуса пользователя
def set_user_state(u_id, state):
    u = User.objects.get(user_id=u_id)
    u.modify(state=state)


# изменить текущий(заполняемый) день
def set_user_day(u_id, day):
    u = User.objects.get(user_id=u_id)
    return u.modify(day=day)


# установить текущим днем предыдущий
def decrease_user_day(u_id):
    u = User.objects.get(user_id=u_id)
    return u.modify(day=u.day - 1)


# ----- блок с функциями проверки "is in" ------


# проверка, есть ли уже продукт в перечне доступных продуктов
def is_in_available_products(user, product_name):
    for av_p in user.available_products:
        if av_p.name == product_name:
            return av_p
    return False


# проверка, есть ли уже продукт в корзине(независимый от рецепта)
def is_in_separate_products(user, product_name):
    for av_p in user.separate_products:
        if av_p.name == product_name:
            return av_p
    return False


# проверка, есть ли уже информация об этом дне
def is_exist_day(user, day_date):
    for day in user.full_plan:
        if day.date == day_date:
            return day
    return False


# проверка, есть ли рецепт в плане на день
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


# ----- get функции -----

# получить всю информацию о конкретном дне
def get_day(user, day_date):
    for day in user.full_plan:
        if day.date == day_date:
            return day
    return 0


# получение state пользователя
def get_user_state(u_id):
    u = User.objects.get(user_id=u_id)
    return u.state


# получение количества дней, для которых составляется/составлен рацион
def get_user_n_days(u_id):
    u = User.objects.get(user_id=u_id)
    return u.n_days


# получить текущий день, по которому выполняется заполнение информации
def get_user_day(u_id):
    u = User.objects.get(user_id=u_id)
    return u.day


# ------ функции для получения данных ------

# получить перечень рецептов о конкретном дне
# возвращает словарь (имя:описание рецепта)
def give_single_day_recipes(u_id, date):
    u = User.objects.get(user_id=u_id)
    this_day = get_day(u, date)
    return_res = {}
    for rec in this_day.recipes:
        return_res[rec.name] = rec.description
    return return_res


# получить перечень всех рецептов
# возвращает словарь (дата:(словарь с описанием рецептов))
def give_all_recipes(u_id):
    res_dict = {}
    day_name = {}
    u = User.objects.get(user_id=u_id)
    for day in u.full_plan:
        res_dict[day.date] = give_single_day_recipes(u_id, day.date)
        day_name[day.date] = day.day
    return res_dict, day_name


# получение всей продуктовой корзины
# возвращает словарь продукт:([количество, единица измерения, нужно ли купить немного больше])
def give_grocery_list(u_id):
    dict_grocery = {}
    u = User.objects.get(user_id=u_id)
    for day_rec in u.full_plan:
        for rec in day_rec.recipes:
            for prod in rec.products:
                if prod.name in dict_grocery:
                    el = dict_grocery[prod.name]
                    if prod.unit != 'none':
                        el[0] += prod.quantity*rec.portion_count
                    el[2] = el[2] or prod.has_null_parts
                    dict_grocery[prod.name] = el
                else:
                    if prod.unit == 'none':
                        qua = 0
                    else:
                        qua = prod.quantity * rec.portion_count
                    dict_grocery[prod.name] = [qua, prod.unit, prod.has_null_parts]
    for cep_prod in u.separate_products:
        if cep_prod.name in dict_grocery:
            el = dict_grocery[cep_prod.name]
            if cep_prod.unit != 'none':
                el[0] += cep_prod.quantity
            el[2] = el[2] or cep_prod.has_null_parts
            dict_grocery[cep_prod.name] = el
        else:
            if cep_prod.unit == 'none':
                qua = 0
            else:
                qua = cep_prod.quantity
            dict_grocery[cep_prod.name] = [qua, cep_prod.unit, cep_prod.has_null_parts]
    for av_prod in u.available_products:
        if av_prod.unit == 'none':
            continue
        if av_prod.name in dict_grocery:
            el = dict_grocery[av_prod.name]
            el[0] -= av_prod.quantity
            if el[0] <= 0 and not av_prod.has_null_parts:
                dict_grocery.pop(av_prod.name)
            elif el[0] <= 0 and av_prod.has_null_parts:
                el[0] = 0
                el[2] = True
                dict_grocery[av_prod.name] = el
            else:
                dict_grocery[av_prod.name] = el
    return dict_grocery


# функция вспомогательная, для отладки
# TODO: delete this
def print_all_user_info(u_id):
    u = User.objects.get(user_id=u_id)
    res_str = "User id: " + str(u.user_id) + "; user_plan:"
    for rec in u.full_plan:
        res_str += f' date -{rec.date},'
        res_str += f'rec_count={len(rec.recipes)},'
        res_str += f'rec={rec.recipes}'
    res_str += '; available products:'
    for a_pr in u.available_products:
        res_str += f'product - {a_pr.name},cou = {a_pr.quantity}'
    res_str += '; sep products:'
    for s_pr in u.separate_products:
        res_str += f'sep product - {s_pr.name}, cou = {s_pr.quantity}'
    print(res_str)


# TODO: delete comments
# можно запустить, посмотреть, как работает на тестах
'''
connect_to_base()
User.objects(user_id=16).delete()
tom = make_product('tomato', 3, 'kg')
tom.save()
milk = make_product('milk', 1, 'l')
milk.save()
tom1 = make_product('tomato', 3, 'kg')
tom1.save()
milk1 = make_product('milk', 1, 'l')
milk1.save()

new_user = User(user_id=16, full_plan=[], available_products=[tom, milk], separate_products=[tom1, milk1])
new_user.save()

tom2 = make_product('tomato', 3, 'kg')
tom2.save()
prod1 = make_product('bread', 1, 'kg')
prod2 = make_product('sugar', 0.6, 'kg')
prod3 = make_product('sugar', 0.6, 'none')
add_new_day(16, '2021-05-19', 'Monday')
recipe1 = make_new_recipe('buter', 'vkusno', 2, [prod1, prod2])
recipe2 = make_new_recipe('bu-buter', 'vkusno-o-o', 3, [prod3, tom2])
add_recipe_to_day(16, '2021-05-19', recipe1)
add_recipe_to_day(16, '2021-05-19', recipe2)

print_all_user_info(16)


l = give_grocery_list(16)
print(l)'''
