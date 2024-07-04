import matplotlib.pyplot as plt

samples = [5, 10, 20, 40, 80, 160]
bleu_samples = [5.53, 3.24, 5.65, 5.49, 6.97, 5.94]
bleu_char_ngrams = [3.44, 4.81, 6.19, 6.92, 4.10, 5.08]

plt.figure(figsize=(10, 6))
plt.plot(samples, bleu_samples, marker='o', label='Samples per translation')
plt.plot(samples, bleu_char_ngrams, marker='s', label='Char n-grams (from Arabic)')

plt.xscale('log', base=2)
plt.xlabel('Number of samples / n-grams')
plt.ylabel('BLEU score')
plt.title('BLEU Scores for Different Sampling Methods')
plt.legend()
plt.grid(True)

plt.show()