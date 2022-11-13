"""
Соколов Лев Максимович. КИ21-17/1Б.

Модуль, в котором реализован кольцевой двусвязный список.
Содержит для класса:
    - DoubleLinkedListItem (узел списка)
    - DoubleLinkedList (сам список)
"""

from typing import Union, Iterator, Generator


class DoubleLinkedListItem:
    """
    Класс узла списка.

    Методы:
        * __init__
        * __str__
        * __repr__

    Свойства:
        * next_item
        * previous_item
    """

    def __init__(self, data: object = None) -> None:
        """
        Конструктор класса, создает не привязанный ни к чему узел

        :param data: хранимое значение
        """
        self.data = data
        self.__next_item = None
        self.__previous_item = None

    @property
    def next_item(self) -> Union[None, object]:
        """
        Свойство - геттер, для получения следующего узла списка

        :return: следующий узел
        """
        return self.__next_item

    @next_item.setter
    def next_item(self, value) -> None:
        """
        Свойство - сеттер, для связи текущего узла со следующим и следующего с текущим

        :param value: узел, для присоединения
        :raises ValueError: В случае передачи в value не DoubleLinkedListItem значения
        """
        if not isinstance(value, DoubleLinkedListItem):
            raise ValueError(f"DoubleLinkedListItem expected, got {value.__class__.__name__}")
        self.__next_item = value
        value.__previous_item = self  # pylint: disable=W0212,W0238

    @property
    def previous_item(self) -> Union[None, object]:
        """
        Свойство - геттер, для получения предыдущего узла списка

        :return: следующий узел
        """
        return self.__previous_item

    @previous_item.setter
    def previous_item(self, value) -> None:
        """
        Свойство - сеттер, для связи текущего узла с предыдущим и предыдущего с текущим

        :param value: узел, для присоединения
        :raises ValueError: В случае передачи в value не DoubleLinkedListItem значения
        """
        if not isinstance(value, DoubleLinkedListItem):
            raise ValueError(f"DoubleLinkedListItem expected, got {value.__class__.__name__}")
        self.__previous_item = value
        value.__next_item = self  # pylint: disable=W0212,W0238

    def __str__(self) -> str:
        """
        Метод строкового представления узла

        :return: строка, содержащая информацию о содержимом узла
        """
        return str(self.data)

    def __repr__(self) -> str:
        """
        Метод строкового представления узла

        :return: строка, содержащая информацию о всех полях экземпляра
        """
        return \
            f"""║  value: {self.data}
║  prev: {self.previous_item}
║  next: {self.next_item}
"""


def create_linked_list(nodes_list):
    """
    Функция создания двусвязного списка из списка данных
    :param nodes_list: список данных
    :return: двусвязный список
    """
    new_list = DoubleLinkedList()
    for val in nodes_list:
        new_list.append(val)
    return new_list


class DoubleLinkedList:
    """
    Класс кольцевого двусвязного списка

    Методы:
        * __init__
        * __len__
        * __iter__
        * __getitem__
        * __contains__
        * __reversed__
        * __str__
        * __repr__
        * append_empty
        * append_left
        * append_right
        * append
        * remove
        * insert
        * create_node
        * find_node

    Свойства (геттеры и сеттеры):
        * head
        * tail
    """

    def __init__(self, head: Union[DoubleLinkedListItem, None] = None) -> None:
        """
        Конструктор класса списка
        вычисляет длину полученной цепочки и определяет ее конец как tail

        :param head: узел начала списка
        """

        self.__head = head

        if head is None:
            self.__tail = None
            self.size = 0
        else:
            self.size = 1
            ptr = head
            while ptr.next_item is not None and ptr.next_item != self.head:
                ptr = ptr.next_item
                self.size += 1
            self.tail = ptr

    @property
    def head(self) -> Union[DoubleLinkedListItem, None]:
        """
        Свойство-геттер. Возвращает узел начала.

        :return: узел начала списка
        """

        return self.__head

    @property
    def tail(self) -> Union[DoubleLinkedListItem, None]:
        """
        Свойство-геттер. Возвращает конца начала.

        :return: узел конца списка
        """

        return self.__tail

    @tail.setter
    def tail(self, value: Union[DoubleLinkedListItem, None]) -> None:
        """
        Свойство-сеттер. Позволяет установить значение конца списка

        :param value: узел, который будет являться концом списка
        """

        self.__tail = value

    @head.setter
    def head(self, value: Union[DoubleLinkedListItem, None]) -> None:
        """
        Свойство-сеттер. Позволяет установить значение конца списка

        :param value: узел, который будет являться началом списка
        """

        self.__head = value

    @staticmethod
    def create_node(data: object) -> DoubleLinkedListItem:
        """
        Метод, создающий unlinked узел с переданным значением

        :param data: значение, которое будет храниться в новом узле
        :return: узел, содержащий значение
        """

        return DoubleLinkedListItem(data)

    def find_node(self, data: object) -> DoubleLinkedListItem:
        """
        Метод поиска узла в списке, содержащего переданное значение

        :param data: значение, которое содержит узел списка
        :return: узел, содержащий значение
        :raises ValueError: если узла с переданным значением нет в списке
        """

        for node in self:
            if node.data == data:
                return node
        raise ValueError("data not in list")

    def append_left(self, item: object) -> None:
        """
        Метод добавления значения в начало списка

        :param item: Добавляемое значение
        """

        if not isinstance(item, DoubleLinkedListItem):
            item = self.create_node(item)

        if self.size == 0:
            self._append_empty(item)
            return

        item.next_item = self.head
        self.head.previous_item = item

        item.previous_item = self.tail
        self.tail.next_item = item
        self.head = item
        self.size += 1

    def append_right(self, item: object) -> None:
        """
        Метод добавления значения в конец списка

        :param item: Добавляемое значение
        """

        if not isinstance(item, DoubleLinkedListItem):
            item = self.create_node(item)
        self.append(item)

    def _append_empty(self, item: object) -> None:
        """
        Метод добавления значения в пустой список

        :param item: Добавляемое значение
        """

        if not isinstance(item, DoubleLinkedListItem):
            item = self.create_node(item)
        self.head = item
        self.head.next_item = item
        self.tail = self.head
        self.size = 1

    def append(self, item: object) -> None:
        """
        Метод добавления значения в конец списка

        :param item: Добавляемое значение
        """

        if not isinstance(item, DoubleLinkedListItem):
            item = self.create_node(item)
        if self.size == 0:
            self._append_empty(item)
            return

        self.tail.next_item = item
        self.tail = item
        self.tail.next_item = self.head
        self.head.previous_item = self.tail
        self.size += 1

    def remove(self, item: object) -> None:
        """
        Метод удаления из списка по значению

        :param item: удаляемое значение
        """

        if not isinstance(item, DoubleLinkedListItem):
            item = self.find_node(item)
        if self.head == item:
            self.head = item.next_item
        if self.tail == item:
            self.tail = item.previous_item
        if self.size == 1:
            self.head, self.tail, self.size = None, None, 0
            del item
            return
        prev_ptr, next_ptr = item.previous_item, item.next_item
        prev_ptr.next_item = next_ptr
        next_ptr.previous_item = prev_ptr
        del item
        self.size -= 1

    def insert(self, previous: object, item: object) -> None:
        """
        Метод вставки значения после переданного

        :param item: вставляемое значение
        :param previous: значение, после которого вставляем
        """

        if not isinstance(item, DoubleLinkedListItem):
            item = self.create_node(item)
        if not isinstance(previous, DoubleLinkedListItem):
            previous = self.find_node(previous)

        next_ptr = previous.next_item
        next_ptr.previous_item = item

        previous.next_item = item

        item.previous_item = previous
        item.next_item = next_ptr
        self.size += 1

    def swap(self, first_item: DoubleLinkedListItem, second_item: DoubleLinkedListItem) -> None:
        """
        Метод обмена двух любых нод списка между собой
        :param first_item: первая нода
        :param second_item: вторая нода
        """

        if first_item == self.__head:
            self.__head = second_item
        elif second_item == self.__head:
            self.__head = first_item
        if first_item == self.__tail:
            self.__tail = second_item
        elif second_item == self.__tail:
            self.__tail = first_item

        temp = first_item.next_item
        first_item.next_item = second_item.next_item
        second_item.next_item = temp

        if first_item.next_item is not None:
            first_item.next_item.previous_item = first_item
        if second_item.next_item is not None:
            second_item.next_item.previous_item = second_item

        temp = first_item.previous_item
        first_item.previous_item = second_item.previous_item
        second_item.previous_item = temp

        if first_item.previous_item is not None:
            first_item.previous_item.next_item = first_item
        if second_item.previous_item is not None:
            second_item.previous_item.next_item = second_item

    def __iter__(self) -> Iterator:
        """
        Метод реализации протокола итератора

        :return: объект-итератор, содержащий узлы списка
        :raises StopIteration: при завершении списка
        """

        temp_pointer = self.head
        for _ in range(self.size):
            yield temp_pointer
            temp_pointer = temp_pointer.next_item

    def __len__(self) -> int:
        """
        Вычисление длины списка

        :return: длина списка
        """

        return self.size

    def __getitem__(self, index: int) -> object:
        """
        Метод, для обращения к элементам списка по индексу

        :param index: индекс элемента, к которому хотим обратиться
        :return: значение data хранимое в узле, располагающемся по заданному индексу
        :raises IndexError: если значение индекса выходит за пределы списка
        """

        if index >= self.size or abs(index) > self.size:
            raise IndexError("index out of range")
        if index >= 0:
            ptr = self.head
            for _ in range(index):
                ptr = ptr.next_item
        else:
            ptr = self.tail
            for _ in range(-1, index, -1):
                ptr = ptr.previous_item
        return ptr.data

    def __contains__(self, item: object) -> bool:
        """
        Метод, для проверки вхождения item в список

        :param item: Значение узла или узел для проверки
        :return: True если значение или узел есть в списке False если нет
        """

        is_contain = False

        for list_item in self:
            if item in (list_item, list_item.data):
                is_contain = True
                break
        return is_contain

    def __reversed__(self) -> Generator:
        """
        Метод, создающий генератор, содержащий узлы списка в обратном порядке

        :return: следующий узел развернутого списка
        """

        ptr = self.tail
        for _ in range(self.size):
            yield ptr
            ptr = ptr.previous_item

    def __repr__(self) -> str:
        """
        Метод строкового представления экземпляра списка

        :return: строка содержащая расширенную информацию о списке
        """

        res = []
        for item in self:
            res.append(repr(item))
        params = f"╠═══════════\n" \
                 f"║->size = {self.size}\n" \
                 f"║->head = {self.head}\n" \
                 f"║->tail = {self.tail}\n" \
                 f"╚═══════════\n"
        return '╔═══════════\n' + '╠═══════════\n'.join(res) + params

    def __str__(self):
        """
        Метод строкового представления экземпляра списка

        :return: строка содержащая информацию о списке
        и хранимых в нем элементах
        """
        str_list = "\n".join([' ' * 11 + str(i) for i in self])
        return f'{self.__class__.__name__}' \
               f'(size: {self.size},\ncontains: [\n' + str_list + '\n])'


if __name__ == '__main__':
    lst = create_linked_list(range(1, 5))
    print(str(lst))
    lst.swap(0, 3)
    print(str(lst))
