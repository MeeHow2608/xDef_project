### **index**: indeks klatki w tracab
### **start**: indeks klatki 5s przed zdarzeniem
### **end**: indeks klatki 5s po zdarzeniu
### **FrameCount**: indeks FrameCount z danych tracab tf_10
### **interceptionSuccess**: boolean, True jeśli przez 3 sekundy drużyna dokonująca przechwytu utrzymała się przy piłce
### **passLength**: długość podania
### **passLineDist**: odległość najbliższego zawodnika przeciwnej drużyny od linii podania
### **passDistance**: odległość najbliższego zawodnika przeciwnej drużyny od podającego
### **receiverDistance**: odległość najbliższego zawodnika przeciwnej drużyny od adresata podania
### **interceptionDistancePassMoment**: odległość (w momencie podania) najbliższego zawodnika z tej samej drużyny od piłkarza dokonującego przechwytu 
### **interceptionDistance**: odległość najbliższego zawodnika z tej samej drużyny od piłkarza dokonującego przechwytu 
### **passLineDistanceBeforePass**: odległość od linii podania zawodnika, który dokonał przechwytu 15klatek* przed podaniem
### **passLineDistanceMomentOfPass**: odległość od linii podania zawodnika, który dokonał przechwytu w momencie podania
### **passLineDistanceAfterPass**: odległość od linii podania zawodnika, który dokonał przechwytu 15klatek* po podaniu
### **passDistanceAfterPass, passDistanceMomentOfPass, passDistanceAfterPass**: odległości od podającego zawodnika, który dokonał przechwytu w tych samych momentach, co wyżej
### **receiverDistanceAfterPass, receiverDistanceMomentOfPass, receiverDistanceAfterPass**: odległości od adresata podania zawodnika, który dokonał przechwytu w tych samych momentach, co wyżej
### **underPressure**: Boolean – czy zawodnik był pressowany (ze statsbomb)
### **playersNearPass**: dane tracab o zawodnikach znajdujących się 1 metr od podającego
### **playersNearRec**: dane tracab o zawodnikach znajdujących się 5 metrów lub ¼ długości podania od adresata podania
### **playersInArea**: informacje tracab o piłkarzach znajdujących się w obszarze potencjalnych przechwytów (trójkąt)
### **playersNearInterceptionPassMoment**: informacje tracab o piłkarzach znajdujących się 3 metry od zawodnika przechwytującego piłkę w momencie podania
### **playersNearInterception**: informacje tracab o piłkarzach znajdujących się 3 metry od zawodnika przechwytującego piłkę w momencie przechwytu
### **passEventTracabFrame**: klatka tracab analizowanego podania
### **passEvent**: event podania, które zostało przechwycone:
##### - id eventu,
##### - typ eventu, 
##### - lokalizacja, 
##### - piłkarz
### **previousEvent**: event poprzedzający podanie,
##### te same informacje jak w passEvent
### **secondPreviousEvent**: event poprzedzający previousEvent,
##### te same informacje jak w passEvent
### **Y**: czy przechwyt był udany (czy jest zapisany jako zdarzenie Interception w danych statsbomb)

## Wszystkie odległości i lokalizacje podawane są w jednostkach tracab (85 jednostek : 1 metr)




