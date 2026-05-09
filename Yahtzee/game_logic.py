import collections

def calculate_points(dice, category):
    if not dice: return 0
    
    counts = collections.Counter(dice)
    unique_dice = sorted(list(set(dice)))
    
    # Sayı bazlı kategoriler (Ones, Twos vb.) zaten dice.count() kullandığı için 
    # liste uzunluğu fark etmeksizin doğru çalışacaktır.
    categories_map = {"Ones": 1, "Twos": 2, "Threes": 3, "Fours": 4, "Fives": 5, "Sixes": 6}
    if category in categories_map:
        return dice.count(categories_map[category]) * categories_map[category]

    # Kombinasyonlar (Sadece seçili zarlar üzerinden kontrol edilir)
    if category == "Three of a kind":
        # Seçili zarlar içinde 3 tane aynı varsa, o seçili zarların toplamını dön
        return sum(dice) if any(v >= 3 for v in counts.values()) else 0
        
    if category == "Four of a kind":
        return sum(dice) if any(v >= 4 for v in counts.values()) else 0
    
    if category == "Full House":
        # Eğer sadece 4 zar seçiliyse Full House imkansız olabilir (isteğine göre ayarla)
        return 25 if sorted(counts.values()) == [2, 3] else 0

    if category == "Small straight":
        straights = [{1,2,3,4}, {2,3,4,5}, {3,4,5,6}]
        return 30 if any(s.issubset(set(dice)) for s in straights) else 0

    if category == "Large straight":
        return 40 if unique_dice in [[1,2,3,4,5], [2,3,4,5,6]] else 0

    if category == "YAHTZEE":
        return 50 if len(unique_dice) == 1 else 0

    if category == "Chance":
        return sum(dice)

    return 0