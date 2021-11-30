from dataclasses import dataclass
from dataclasses_json import dataclass_json
from typing import List


@dataclass_json
@dataclass(frozen=True)
class Product:
    name: str
    quantity: int
    units: str


@dataclass_json
@dataclass(frozen=True)
class Recipe:
    name: str
    products: List[Product]


# @dataclass_json
# @dataclass(frozen=True)
# class AvailableProducts:
#     available_products: List[Product]
#
#
# @dataclass_json
# @dataclass(frozen=True)
# class SeparateProducts:
#     separate_products: List[Product]


@dataclass_json
@dataclass(frozen=True)
class DayPlan:
    date: str
    day: str
    recipes: List[Recipe]


@dataclass_json
@dataclass(frozen=True)
class User:
    id: int
    plan: List[DayPlan]
    available_products: List[Product]
    separate_products: List[Product]

    def show_grocery_list(self):
        dct = {}
        for day_plan in self.plan:
            for recipe in day_plan.recipes:
                for product in recipe.products:
                    if product.name in dct:
                        dct[product.name] += product.quantity
                    else:
                        dct[product.name] = product.quantity

        for product in self.separate_products:
            if product.name in dct:
                dct[product.name] += product.quantity

        for product in self.available_products:
            if product.name in dct:
                dct[product.name] -= min(product.quantity, dct[product.name])
        return dct


if __name__ == '__main__':
    data = '''{
  "id": 83936171,
  "plan": [
    {
      "date": "03-12-2021",
      "day": "Friday",
      "recipes": [
        {
          "name": "Lasagna",
          "url": "weefwef2",
          "products": [
            {
              "name": "cheese",
              "quantity": 100,
              "units": "g"
            },
            {
              "name": "milk",
              "quantity": 1,
              "units": "l"
            }
          ]
        },
        {
          "name": "Meat balls",
          "url": "weefwef1",
          "products": [
            {
              "name": "meat",
              "quantity": 1,
              "units": "kg"
            },
            {
              "name": "riсe",
              "quantity": 0.5,
              "units": "kg"
            },
            {
              "name": "cheese",
              "quantity": 200,
              "units": "g"
            }
          ]
        }
      ]
    }
  ],
  "separate_products": [
    {
      "name": "chocolate",
      "quantity": 1,
      "units": "u"
    },
    {
      "name": "cheese",
      "quantity": 500,
      "units": "g"
    }
  ],
  "available_products": [
    {
      "name": "cheese",
      "quantity": 50,
      "units": "g"
    },
    {
      "name": "bread",
      "quantity": 1,
      "units": "kg"
    }
  ]
}'''.strip()

    user = User.from_json(data)

    print(user.show_grocery_list())

    # print(user.to_json(indent=4))
