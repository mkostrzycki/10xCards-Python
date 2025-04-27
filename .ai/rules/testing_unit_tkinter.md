## Mockowanie mainloop

Jednym z najczęstszych problemów jest blokada testów przez mainloop. Aby temu zapobiec, można mockować metodę mainloop:
```python
import pytest
import tkinter as tk

def test_mainloop_not_called(mocker):
    mocker.patch('tkinter.Tk.mainloop', return_value=None)
    app = tk.Tk()
    app.mainloop()
    tkinter.Tk.mainloop.assert_called_once()
```
W tym przypadku mocker.patch zastępuje mainloop mockiem, który nie wykonuje rzeczywistej pętli zdarzeń, co pozwala na kontynuowanie testu.

## Mockowanie widgetów

Jeśli testujesz funkcję, która korzysta z widgetów, takich jak Entry czy Listbox, możesz stworzyć mocki tych obiektów. Przykładowo:
```python
def test_add_item(mocker):
    entry = mocker.Mock()
    entry.get.return_value = "Test Item"
    listbox = mocker.Mock()
    def add_item(entry, listbox):
        item = entry.get()
        listbox.insert(tk.END, item)
    add_item(entry, listbox)
    listbox.insert.assert_called_once_with(tk.END, "Test Item")
```
Ten przykład pokazuje, jak mockować widgety i sprawdzać, czy metody, takie jak insert, zostały wywołane poprawnie.

## Mockowanie klas tkinter

Jeśli Twoja aplikacja tworzy instancje klas, takich jak tkinter.Tk, możesz mockować całą klasę:
```python
def test_tkinter_module(mocker):
    mocker.patch('tkinter.Tk', return_value=MagicMock())
    app = tk.Tk()
    assert isinstance(app, MagicMock)
```
Tutaj mocker.patch zastępuje klasę tkinter.Tk mockiem, co pozwala na testowanie kodu, który tworzy instancje, bez rzeczywistego GUI.

## Wskazówki i ograniczenia

 - Unikaj uruchamiania mainloop: Zawsze mockuj mainloop, jeśli Twoja aplikacja go używa, aby testy nie były blokowane.
 - Sprawdzaj wywołania metod: Po mockowaniu, używaj metod takich jak assert_called_once_with, aby zweryfikować, czy metody zostały wywołane poprawnie.
 - Testuj logikę, nie GUI: Mockowanie pozwala skupić się na testowaniu logiki biznesowej aplikacji, a nie na samym interfejsie użytkownika.