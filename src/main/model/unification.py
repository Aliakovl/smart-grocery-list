
dict_for_glass = {
    'сахар': '200',
    'крахмал': '160',
    'мука': '160',
    'молоко': '250',
    'мед': '415',
    'масло': '225',
    'вода': '200',
    'сливки': '230',
    'сметана': '230',
    'рис': '180',
    'гречка': '165',
    'манка': '160'
}

dict_for_tablespoon = {
    'сахар': '25',
    'крахмал': '12',
    'мука': '25',
    'молоко': '20',
    'мед': '30',
    'масло': '17',
    'желатин': '10',
    'сода': '8,5',
    'томатная паста': '24',
    'соль': '30'

}

dict_for_teaspoon = {
    'сахар': '8',
    'крахмал': '6',
    'мука': '8',
    'молоко': '5',
    'мед': '9',
    'масло': '5',
    'соль': '10'
}

dict_of_products = {
    'стакан': dict_for_glass,
    'столовая ложка': dict_for_tablespoon,
    'чайная ложка': dict_for_teaspoon
}

user_ingr = 'Мука'
user_quantity = 2
user_measure = 'стакан'
user_list = [(user_ingr, user_quantity, user_measure)]


def normalization(user_list):
    found = False
    for i in range(len(user_list)):
        new_measure = 0
        ingrt = user_list[i][0].lower()
        quantity = user_list[i][1]
        measure = user_list[i][2].lower()

        if dict_of_products.get(measure):
            if measure == 'чайная ложка':
                meas = dict_of_products['чайная ложка'][ingrt]
                new_measure = float(meas) * quantity

            if measure == 'столовая ложка':
                meas = dict_of_products['столовая ложка'][ingrt]
                new_measure = float(meas) * quantity

            if measure == 'стакан':
                meas = dict_of_products['стакан'][ingrt]
                new_measure = float(meas) * quantity
            else:
                continue
            user_list[i] = (ingrt, new_measure, 'граммы')


normalization(user_list)


user_list
