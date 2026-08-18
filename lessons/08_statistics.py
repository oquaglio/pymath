# %% [markdown]
# # 8. Statistics and probability

# %%
from pymath import *  # noqa: F403

# %% [markdown]
# ## Describing data
#
# One call gives every summary statistic. Note there are **two** standard
# deviations:
#
# * `sd_population` (÷n) — you have the whole population (the σ key)
# * `sd_sample` (÷n−1) — you have a sample of a bigger group (the s key)
#
# Use the sample one unless you truly measured everything.

# %%
marks = [52, 61, 68, 71, 71, 74, 78, 82, 85, 91, 95]
show(describe(marks))

# %%
histogram(marks, bins=6, title="Test marks", xlabel="mark")

# %%
boxplot(marks, title="Five-number summary")

# %% [markdown]
# Outliers are flagged by the 1.5×IQR rule — the same rule that draws the
# whiskers on the box plot.

# %%
with_outlier = [*marks, 12]
print(describe(with_outlier)["outliers"])

# %%
boxplot([marks, with_outlier], labels=["clean", "with outlier"], title="Effect of an outlier")

# %% [markdown]
# ## Frequency tables
#
# Grouping continuous data into class intervals:

# %%
print(stats.frequency_table(marks, bins=5))

# %% [markdown]
# ## Probability distributions
#
# ### Binomial — fixed number of trials, each success or failure
#
# "Toss a fair coin 10 times."

# %%
b = binomial(n=10, p=0.5)
print("P(exactly 5 heads)  =", b["exactly"](5))
print("P(at most 3 heads)  =", b["at_most"](3))
print("P(at least 8 heads) =", b["at_least"](8))
print("mean =", b["mean"], " sd =", b["sd"])

# %% [markdown]
# ### Normal — the bell curve
#
# The calculator's P/Q/R functions, by name.

# %%
iq = normal_dist(mean=100, sd=15)
print("P(X < 115)      =", iq["below"](115))
print("P(X > 130)      =", iq["above"](130))
print("P(85 < X < 115) =", iq["between"](85, 115))
print("top 5% starts at:", iq["inverse"](0.95))
print("z-score of 130:  ", iq["z"](130))

# %%
plot_normal(100, 15, shade=(85, 115), title="IQ: one standard deviation either side")

# %% [markdown]
# The 68–95–99.7 rule falls straight out:

# %%
for k in (1, 2, 3):
    print(f"within {k} sd: {iq['between'](100 - k * 15, 100 + k * 15):.4f}")

# %% [markdown]
# ### Poisson — counts of rare events in a fixed interval

# %%
calls = poisson(rate=3)  # 3 calls per hour on average
print("P(exactly 0) =", calls["exactly"](0))
print("P(5 or more) =", calls["at_least"](5))

# %% [markdown]
# ## Counting
#
# Permutations care about order; combinations don't.

# %%
print("nPr(5,2) =", nPr(5, 2), "— ordered")
print("nCr(5,2) =", nCr(5, 2), "— unordered")
print("lottery odds, 6 from 45: 1 in", nCr(45, 6))
print(stats.list_combinations("ABCD", 2))

# %% [markdown]
# ## Regression — fitting a model to data
#
# `r_squared` is the fraction of the variation the model explains; 1.0 is a
# perfect fit.

# %%
hours = [1, 2, 3, 4, 5, 6, 7, 8]
scores = [52, 55, 61, 64, 70, 72, 78, 85]
model = regression(hours, scores)
show(model)

# %%
scatter(hours, scores, fit="linear", title="Study hours vs score",
        xlabel="hours studied", ylabel="score")

# %%
print("predicted score for 10 hours:", model["predict"](10))

# %% [markdown]
# ### Non-linear models
#
# Not everything is a line. Bacterial growth is exponential:

# %%
time = [0, 1, 2, 3, 4, 5]
count = [100, 165, 270, 445, 735, 1210]
exp_model = regression(time, count, kind="exponential")
print(exp_model["equation"], " R² =", exp_model["r_squared"])

# %%
scatter(time, count, fit="exponential", title="Bacterial growth",
        xlabel="hours", ylabel="count")

# %% [markdown]
# Compare fits by R² — but beware: a more flexible model always fits the
# *sample* better, which isn't the same as being more true.

# %%
for kind in ["linear", "quadratic", "exponential", "power"]:
    print(f"{kind:12} R² = {regression(time[1:], count[1:], kind)['r_squared']:.6f}")

# %% [markdown]
# ## Correlation is not causation
#
# Pearson measures *linear* association; Spearman measures whether the ranks
# move together, which catches curved relationships too.

# %%
show(correlation(hours, scores))

# %%
# Perfectly related, but not linearly — Pearson understates it, Spearman doesn't.
show(correlation([1, 2, 3, 4, 5], [1, 4, 9, 16, 25]))

# %% [markdown]
# ## Confidence intervals
#
# "The mean is 11.6, and we're 95% confident the true mean lies in this range."

# %%
sample = [10, 12, 11, 13, 12, 14, 10, 11]
show(confidence_interval(sample, confidence=0.95))
show(confidence_interval(sample, confidence=0.99))  # more confidence → wider

# %% [markdown]
# ## Hypothesis testing
#
# A small p-value (< 0.05 by convention) is evidence *against* the null
# hypothesis that nothing is going on.

# %%
group_a = [72, 75, 68, 71, 74, 70, 73]
group_b = [78, 82, 79, 85, 80, 83, 81]
show(hypothesis_test(group_a, group_b))

# %%
# One-sample: is this sample's mean different from 70?
show(hypothesis_test(group_a, popmean=70))
