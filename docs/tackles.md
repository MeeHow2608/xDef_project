### **index**: indeks klatki w tracab
### **start**: indeks klatki 5s przed zdarzeniem
### **end**: indeks klatki 5s po zdarzeniu
### **FrameCount**: indeks FrameCount z danych tracab tf_10
### **playerID**: id statsbomb gracza
### **playerName**: imię i nazwisko gracza
### **location**: lokalizacja zdarzenia
### **eventType**: typ zdarzenia odbioru - możliwe wartości: Duel i Dribble
### **prevEventType**: typ poprzedniego zdarzenia - możliwe zdarzenia: Dribble i Disspossed dla Duel, Dribbled Past dla Dribble
### **possessionChanges**: liczba zmian posiadania piłki
### **isCF**: czy zawodnik, któremu odbierana jest piłka jest napastnikiem
### **tackleZone**: obszar boiska, gdzie ma miejsce zdarzenie
### **attackersDefendersRatio**: stosunek zawodników drużyny przy piłce do zawodników drużyny przeciwnej
### **underPressure**: Boolean - czy zawodnik był pressowany JESZCZE PRZED ODBIOREM PIŁKI (ze statsbomb)
### **playersNear2m**: dane tracab o graczach w obszarze 2 metrów od piłkarza dokonującego odbioru piłki
### **playersNear4m**: dane tracab o graczach w obszarze 4 metrów od piłkarza dokonującego odbioru piłki
### **preTackleEvent**: informacje o evencie poprzedzającym odbiór (możliwe typy - patrz prevEventType) :
##### - id eventu,
##### - typ eventu, 
##### - lokalizacja, 
##### - piłkarz
### **previousEvent**: event poprzedzający preTackleEvent,
##### te same informacje jak w preTackleEvent
### **secondPreviousEvent**: event poprzedzający previousEvent,
##### te same informacje jak w preTackleEvent
### **Y**: czy odbiór był udany (czy wystapiło zdarzenie Duel czy Dribbled Past)

## Wszystkie odległości i lokalizacje podawane są w jednostkach tracab (85 jednostek : 1 metr)




