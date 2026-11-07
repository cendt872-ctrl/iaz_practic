# # Практична робота 4.13: Використання репозиторіїв аналітичних моделей (Transfer Learning та Reinforcement Learning)
pip install torch torchvision
import numpy as np

print("=== Частина 1: Перевірка концепції Transfer Learning (ResNet50) ===")
try:
    import torch
    import torch.nn as nn
    from torchvision import models
    
    # Завантаження попередньо навченої моделі ResNet50
    model = models.resnet50(weights=models.ResNet50_Weights.DEFAULT)
    for param in model.parameters():
        param.requires_grad = False
        
    num_ftrs = model.fc.in_features
    model.fc = nn.Linear(num_ftrs, 3)
    print("✔ Модель ResNet50 успішно адаптована (Fine-Tuning налаштовано).")
except ImportError:
    print("ℹ Бібліотека PyTorch не встановлена у поточному середовищі. Логіку Transfer Learning налаштовано умовно.")

print("\n=== Частина 2: Демонстрація середовища RL для логістики (LogisticsEnv) ===")
class LogisticsEnv:
    """Просте симульоване середовище для оптимізації логістичних маршрутів в умовах ІАЗ ОВУ."""
    def __init__(self):
        self.state = np.array([0, 0])
        self.goal = np.array([9, 9])
        
    def reset(self):
        self.state = np.array([0, 0])
        return self.state
        
    def step(self, action):
        # 0: Вгору, 1: Вниз, 2: Вліво, 3: Вправо
        if action == 0: self.state[1] = min(self.state[1] + 1, 9)
        elif action == 1: self.state[1] = max(self.state[1] - 1, 0)
        elif action == 2: self.state[0] = max(self.state[0] - 1, 0)
        elif action == 3: self.state[0] = min(self.state[0] + 1, 9)
        
        done = np.array_equal(self.state, self.goal)
        reward = 10 if done else -1
        return self.state, reward, done

env = LogisticsEnv()
state = env.reset()
print(f"Початковий стан агента: {state}, Ціль: {env.goal}")
next_state, reward, done = env.step(3) # Дія: Вправо
print(f"Після дії Вправо -> Стан: {next_state}, Нагорода: {reward}")
print("\n✔ Практичний скрипт 4.13 успішно виконано!")