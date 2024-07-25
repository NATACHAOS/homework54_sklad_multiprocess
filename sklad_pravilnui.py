import multiprocessing as mp
import re

"""Моделирование программы для управления данными о движении товаров на складе и эффективной 
обработки запросов на обновление информации в многопользовательской среде.

Представим, что у вас есть система управления складом, где каждую минуту поступают запросы 
на обновление информации о поступлении товаров и отгрузке товаров.
Наша задача заключается в разработке программы, которая будет эффективно обрабатывать эти 
запросы в многопользовательской среде, с использованием механизма мультипроцессорности 
для обеспечения быстрой реакции на поступающие данные.

Создайте класс WarehouseManager - менеджера склада, который будет обладать следующими свойствами:
Атрибут data - словарь, где ключ - название продукта, а значение - его кол-во. (изначально пустой)
Метод process_request - реализует запрос (действие с товаром), принимая request - кортеж.
Есть 2 действия: receipt - получение, shipment - отгрузка.
а) В случае получения данные должны поступить в data (добавить пару, если её не было и 
изменить значение ключа, если позиция уже была в словаре)
б) В случае отгрузки данные товара должны уменьшаться (если товар есть в data и если товара больше чем 0).

3.Метод run - принимает запросы и создаёт для каждого свой параллельный процесс, запускает его(start) 
и замораживает(join)."""

class WareHouseManager:

    result = []
    data_ = {}
    key = []
    val = []
    dock = []
    quantity = 0
    data_list = []

    def process_request(self, request):
        """ Определяет результат остатков на складе - из полученных вычитает отгрузку"""
        # print("length request", len(request))
        text = re.compile(r"[a-z]+")
        text_1 = re.findall(text, "product")
        text_2 = re.findall(text, "shipment")
        text_3 = re.findall(text, "receipt")
        """Создаем списки продуктов, их количества, прибытия и убытия продуктов"""
        for i in range(len(request)):
            if type(request[i]) == int:
                quantity = request[i]
                self.val.append(quantity)
            elif type(request[i]) == str and text_1[0] in request[i]:
                self.key.append(request[i])
            elif type(request[i]) == str and (text_2[0] in request[i] or text_3[0] in request[i]):
                # value = request[i]
                self.dock.append(request[i])
        print("keys = ", self.key)
        print("vals = ", self.val)
        print("dock = ", self.dock)
        """Производим учет отгруженных продуктов и создаем словарь с остатками на складе."""
        for k in range(len(self.key)):
            if self.dock[k] == "receipt":
                self.data_.update({self.key[k]: self.val[k]})
            if self.dock[k] == "shipment":
                for key in self.data_.keys():  # Берем уже имеющийся словарь и проверяем на совпадающие ключи
                    if key == self.key[k]:
                        old_dict = {key: self.data_.get(key)}  # Найденое старое значение из уже созданного словаря
                        new_dict = {self.key[k]: self.val[k]}  # Новое значение которое надо вычесть из уже имеющегося
                        new_val = (old_dict.get(key) - new_dict.get(self.key[k]))
                        self.data_.update({self.key[k]: new_val})
        print(self.data_)
        return self.data_

    def run(self, requests):
        """ Запускаем Pool с двумя процессами"""
        print('Starting', mp.current_process().name)
        request = []
        for i in range(len(requests)):
            request.append(list(requests[i]))
        print("run request", request)
        with mp.Pool(processes=2) as pool:
            """Pool корректно работает при одном процессе, при process=2 необходимо прогонять 
            несколько раз для получения полного результата, соответсвующего примеру"""
            result = pool.map(self.process_request, request)
            pool.close()
            pool.join()

        last_result = result[-1]  # Так как результат Pool в данном случае есть список кортежей, то берем последний
        print("Состояние продуктов на складе: ", last_result)


if __name__ == '__main__':
    requests = [
        ("product1", "receipt", 100),
        ("product2", "receipt", 150),
        ("product1", "shipment", 30),
        ("product3", "receipt", 200),
        ("product2", "shipment", 50)
    ]

    manager = WareHouseManager()
    manager.run(requests)