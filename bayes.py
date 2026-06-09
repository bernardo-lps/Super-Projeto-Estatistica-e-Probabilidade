{
 "cells": [
  {
   "cell_type": "code",
   "execution_count": 2,
   "id": "f48fc3a4",
   "metadata": {},
   "outputs": [],
   "source": [
    "import pandas as pd\n",
    "import matplotlib.pyplot as plt\n",
    "import seaborn as sb"
   ]
  },
  {
   "cell_type": "code",
   "execution_count": null,
   "id": "b62a899b",
   "metadata": {},
   "outputs": [],
   "source": [
    "# Carregando os dados\n",
    "df = pd.read_csv('student_habits_performance.csv')\n",
    "\n",
    "# Exibindo informações do dataset\n",
    "print(\"Primeiras linhas do dataset:\")\n",
    "print(df.head())\n",
    "print(\"\\nInformações do dataset:\")\n",
    "print(df.info())\n",
    "print(\"\\nEstatísticas descritivas:\")\n",
    "print(df.describe())"
   ]
  }
 ],
 "metadata": {
  "kernelspec": {
   "display_name": "Python 3",
   "language": "python",
   "name": "python3"
  },
  "language_info": {
   "codemirror_mode": {
    "name": "ipython",
    "version": 3
   },
   "file_extension": ".py",
   "mimetype": "text/x-python",
   "name": "python",
   "nbconvert_exporter": "python",
   "pygments_lexer": "ipython3",
   "version": "3.14.0"
  }
 },
 "nbformat": 4,
 "nbformat_minor": 5
}
