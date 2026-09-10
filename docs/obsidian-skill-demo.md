---
title: OCTera — модель классификации
date: 2026-09-10
tags:
  - project/octera
  - ml
aliases:
  - OCT Model Notes
status: in-progress
---

# OCTera — модель классификации

Используется предобученная модель [[tomalmog-oct-retinal-classifier|oct-retinal-classifier]] (EfficientNet-B3), дообученная на датасете Kermany под 4 класса.

> [!info] Точность
> ==99.6% на тестовой выборке автора модели==. Клинически не валидирована.

## Классы

- [ ] CNV
- [ ] DME
- [ ] DRUSEN
- [ ] NORMAL

## Связанные заметки

См. также [[Backend API#Эндпоинты]] и [[Открытые вопросы]].

%% Это скрытый комментарий — не отображается в reading view %%
