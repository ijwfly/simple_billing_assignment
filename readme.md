# Simple Billing test assignment
1. Один кошелёк для одного клиента
2. Хранится информация о кошельке и остатке средств на нём
3. Основные операции:
- создание клиентского кошелька
- зачисление денежных средств на кошелек
- списание средств
- p2p перевод денежных средств с одного кошелька на другой

## Идеи
### Готово
- hmac-подпись запросов (предполагаем, что сервис находится внутри доверенной сети, достаточно подписи)
- блокировка на счёт через select for update
### Не готово 
- идемпотентность методов по operation_id (в redis)

## Хорошо бы сделать
- механизм изменения баланса через хранение промежуточных состояний (возможно убрать блокировку с механизма начисления средств)
- сгенерированный строковый идентификатор кошелька
- возвращать баланс после пополнения/списания с кошелька
