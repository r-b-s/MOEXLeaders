#MOEXLeaders
http://t.me/MOEXLeaders_bot

Бот помощник для активной стратегии покупки бумаг лидеров роста за период (buy winners - sell losers).
Стратегия основана на инертности московской биржи, предположении о том что ликвидные бумаги выросшие за прошедший период с большей вероятностью продолжат рост в следующий период.
Историческая среднегодовая доходность 25%.

Алгоритм торговли без плеч:\n
1) В равные промежутки времени определяем лидеров роста среди самых ликвидных бумаг.\n
2) Продаем имеющиеся бумаги, выпавшие из лидеров. Для оставшихся обновляем стоп-лоссы.\n
3) Докупаем на равные суммы новых лидеров. Ставим стоп-лоссы (рекомендуется вычесть из текущей цены 2-3 среднедневных волатильности).\n
В случае если за период упали 3/4 самых ликвидных бумаг, следует продать весь портфель - выйти в кэш.\n

Рекомендуемые параметры\n
Выбор самых ликвидных бумаг (по обороту): 30-40 (всего на MOEX > 250)\n
Бумаг в портфеле: 7-11\n
Интервал: неделя\n
(Данная информация не является индивидуальной инвестиционной рекомендацией)\n

Usage

/top40d10s3\n
40 самых ликвидных бумаг\n
10 дней\n
3 * волатильность -> стоп-лосс\n

/top30w1s2\n
30 самых ликвидных бумаг\n
1 неделя\n
2 * волатильность -> стоп-лосс\n

/top = /top40w1s2

Output\n
Δ% - рост или падение в процентах\n
LAST - последняя цена (открытый API MOEX имеет 15-минутную задержку)\n
std% - среднеквадратичное отклонение в % (волатильность)\n
Sloss - стоп-лосс\n
