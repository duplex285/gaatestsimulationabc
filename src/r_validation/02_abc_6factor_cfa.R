# ============================================================================
# 02_abc_6factor_cfa.R
# Full ABC 6-Factor CFA Validation
#
# Tests the central structural claim: satisfaction and frustration are
# distinct constructs within each domain (Ambition, Belonging, Craft).
#
# Models compared:
#   6-factor: A-sat, A-frust, B-sat, B-frust, C-sat, C-frust (hypothesised)
#   3-factor: A, B, C (sat/frust collapsed per domain)
#   1-factor: General factor (all items load on one factor)
#
# Reference: abc-assessment-spec Section 11 (Simulation Validation Plan)
# Reference: abc-assessment-spec Section 13.1 (CFA methodology)
# Reference: abc-assessment-spec Section 11.3 (fit thresholds)
# ============================================================================

library(lavaan)
library(MASS)
library(psych)

set.seed(42)  # Rule 7: Reproducibility

cat("\n")
cat("================================================================\n")
cat("  ABC 6-FACTOR CFA VALIDATION (CRITICAL GATE)\n")
cat("================================================================\n\n")

# --------------------------------------------------------------------------
# Step 1: Define population correlation matrix
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 11.1
# Source: Chen et al. (2015), Bartholomew et al. (2011)
# Within-domain sat/frust: r = -0.40 to -0.60
# Cross-domain satisfactions: r = 0.20 to 0.40
# Cross-domain frustrations: r = 0.25 to 0.45
# Cross-domain sat/frust: r = -0.10 to -0.25

factor_names <- c("A_sat", "A_frust", "B_sat", "B_frust", "C_sat", "C_frust")

cor_matrix <- matrix(c(
  # A-sat  A-frust  B-sat  B-frust  C-sat  C-frust
   1.00,  -0.50,   0.30,  -0.15,   0.35,  -0.10,  # A-sat
  -0.50,   1.00,  -0.15,   0.35,  -0.10,   0.40,  # A-frust
   0.30,  -0.15,   1.00,  -0.55,   0.25,  -0.20,  # B-sat
  -0.15,   0.35,  -0.55,   1.00,  -0.10,   0.35,  # B-frust
   0.35,  -0.10,   0.25,  -0.10,   1.00,  -0.45,  # C-sat
  -0.10,   0.40,  -0.20,   0.35,  -0.45,   1.00   # C-frust
), nrow = 6, byrow = TRUE)
rownames(cor_matrix) <- factor_names
colnames(cor_matrix) <- factor_names

cat("Population correlation matrix:\n")
print(round(cor_matrix, 2))
cat("\n")

# Verify positive definite
eigenvalues <- eigen(cor_matrix)$values
cat("Eigenvalues:", paste(round(eigenvalues, 3), collapse = ", "), "\n")
cat("Positive definite:", all(eigenvalues > 0), "\n\n")

# --------------------------------------------------------------------------
# Step 2: Define factor loading matrix
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 13.1
# 24 items: 4 per subscale, loadings 0.60-0.80
# Item 4 of each subscale is reverse-scored (slightly lower loading)

n_items <- 24
n_factors <- 6
n_participants <- 1000

# Loading matrix (24 x 6)
Lambda <- matrix(0, nrow = n_items, ncol = n_factors)

# A-sat items (1-4)
Lambda[1, 1] <- 0.75
Lambda[2, 1] <- 0.72
Lambda[3, 1] <- 0.70
Lambda[4, 1] <- 0.65  # reverse-scored item, slightly lower

# A-frust items (5-8)
Lambda[5, 2] <- 0.74
Lambda[6, 2] <- 0.71
Lambda[7, 2] <- 0.73
Lambda[8, 2] <- 0.66  # reverse-scored

# B-sat items (9-12)
Lambda[9, 3]  <- 0.73
Lambda[10, 3] <- 0.70
Lambda[11, 3] <- 0.68
Lambda[12, 3] <- 0.64  # reverse-scored

# B-frust items (13-16)
Lambda[13, 4] <- 0.76
Lambda[14, 4] <- 0.72
Lambda[15, 4] <- 0.69
Lambda[16, 4] <- 0.67  # reverse-scored

# C-sat items (17-20)
Lambda[17, 5] <- 0.74
Lambda[18, 5] <- 0.71
Lambda[19, 5] <- 0.73
Lambda[20, 5] <- 0.63  # reverse-scored

# C-frust items (21-24)
Lambda[21, 6] <- 0.75
Lambda[22, 6] <- 0.70
Lambda[23, 6] <- 0.72
Lambda[24, 6] <- 0.65  # reverse-scored

cat("Factor loading matrix defined (24 items x 6 factors).\n")
cat("Loading range:", round(min(Lambda[Lambda > 0]), 2), "to",
    round(max(Lambda[Lambda > 0]), 2), "\n\n")

# --------------------------------------------------------------------------
# Step 3: Generate model-implied covariance and sample data
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 13.1
# Sigma = Lambda * Phi * Lambda' + Theta

Sigma_model <- Lambda %*% cor_matrix %*% t(Lambda)

# Unique variances: ensure diagonal >= some minimum
diag_unique <- 1 - diag(Sigma_model)
diag_unique <- pmax(diag_unique, 0.15)  # Floor at 0.15
Theta <- diag(diag_unique)

Sigma_total <- Lambda %*% cor_matrix %*% t(Lambda) + Theta

# Force symmetry and positive definiteness
Sigma_total <- (Sigma_total + t(Sigma_total)) / 2
ev <- eigen(Sigma_total)$values
if (any(ev <= 0)) {
  # Small ridge if needed
  Sigma_total <- Sigma_total + diag(0.01, n_items)
}

cat("Generating", n_participants, "simulated participants...\n")

continuous_data <- mvrnorm(n = n_participants, mu = rep(0, n_items), Sigma = Sigma_total)

# --------------------------------------------------------------------------
# Step 4: Discretize to 1-7 Likert scale
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 11.2 / Section 13.1

thresholds <- c(-2.0, -1.2, -0.4, 0.4, 1.2, 2.0)

discretize <- function(x, thresh) {
  result <- rep(1L, length(x))
  for (k in seq_along(thresh)) {
    result <- result + as.integer(x > thresh[k])
  }
  return(result)
}

ordinal_data <- matrix(0L, nrow = n_participants, ncol = n_items)
for (j in 1:n_items) {
  ordinal_data[, j] <- discretize(continuous_data[, j], thresholds)
}

# Name the items
item_names <- c(
  paste0("AS", 1:4), paste0("AF", 1:4),
  paste0("BS", 1:4), paste0("BF", 1:4),
  paste0("CS", 1:4), paste0("CF", 1:4)
)

df <- as.data.frame(ordinal_data)
colnames(df) <- item_names

# Convert to ordered factors for WLSMV
for (col in names(df)) {
  df[[col]] <- ordered(df[[col]])
}

cat("Data generated and discretized.\n")
cat("Dimensions:", nrow(df), "x", ncol(df), "\n")

# Quick distribution check
df_numeric <- as.data.frame(lapply(df, function(x) as.numeric(x)))
cat("Overall response mean:", round(mean(as.matrix(df_numeric)), 2), "\n")
cat("Overall response SD:", round(sd(as.matrix(df_numeric)), 2), "\n\n")

# --------------------------------------------------------------------------
# Step 5: Define three CFA models
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 11.3 (model comparison)

# Model 1: 6-factor (hypothesised)
model_6factor <- '
  A_sat   =~ AS1 + AS2 + AS3 + AS4
  A_frust =~ AF1 + AF2 + AF3 + AF4
  B_sat   =~ BS1 + BS2 + BS3 + BS4
  B_frust =~ BF1 + BF2 + BF3 + BF4
  C_sat   =~ CS1 + CS2 + CS3 + CS4
  C_frust =~ CF1 + CF2 + CF3 + CF4
'

# Model 2: 3-factor (sat/frust collapsed per domain)
model_3factor <- '
  Ambition  =~ AS1 + AS2 + AS3 + AS4 + AF1 + AF2 + AF3 + AF4
  Belonging =~ BS1 + BS2 + BS3 + BS4 + BF1 + BF2 + BF3 + BF4
  Craft     =~ CS1 + CS2 + CS3 + CS4 + CF1 + CF2 + CF3 + CF4
'

# Model 3: 1-factor (general factor)
model_1factor <- '
  General =~ AS1 + AS2 + AS3 + AS4 + AF1 + AF2 + AF3 + AF4 +
             BS1 + BS2 + BS3 + BS4 + BF1 + BF2 + BF3 + BF4 +
             CS1 + CS2 + CS3 + CS4 + CF1 + CF2 + CF3 + CF4
'

# --------------------------------------------------------------------------
# Step 6: Fit all three models
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 13.1 (WLSMV estimator)

cat("================================================================\n")
cat("FITTING CFA MODELS\n")
cat("================================================================\n\n")

cat("Fitting 6-factor model...\n")
fit_6 <- cfa(model_6factor, data = df, ordered = TRUE, estimator = "WLSMV")
cat("  Converged:", lavInspect(fit_6, "converged"), "\n\n")

cat("Fitting 3-factor model...\n")
fit_3 <- cfa(model_3factor, data = df, ordered = TRUE, estimator = "WLSMV")
cat("  Converged:", lavInspect(fit_3, "converged"), "\n\n")

cat("Fitting 1-factor model...\n")
fit_1 <- cfa(model_1factor, data = df, ordered = TRUE, estimator = "WLSMV")
cat("  Converged:", lavInspect(fit_1, "converged"), "\n\n")

# --------------------------------------------------------------------------
# Step 7: Extract fit indices and compare models
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 11.3 (fit thresholds)

extract_fit <- function(fit_obj) {
  fm <- fitMeasures(fit_obj, c("cfi", "tli", "rmsea", "srmr", "chisq", "df", "pvalue"))
  return(fm)
}

fit_6_vals <- extract_fit(fit_6)
fit_3_vals <- extract_fit(fit_3)
fit_1_vals <- extract_fit(fit_1)

cat("================================================================\n")
cat("MODEL COMPARISON\n")
cat("================================================================\n\n")

cat(sprintf("%-10s %8s %8s %8s %8s %10s %6s\n",
            "Model", "CFI", "TLI", "RMSEA", "SRMR", "Chi-sq", "df"))
cat(paste(rep("-", 62), collapse=""), "\n")
cat(sprintf("%-10s %8.3f %8.3f %8.3f %8.3f %10.1f %6.0f\n",
            "6-factor", fit_6_vals["cfi"], fit_6_vals["tli"],
            fit_6_vals["rmsea"], fit_6_vals["srmr"],
            fit_6_vals["chisq"], fit_6_vals["df"]))
cat(sprintf("%-10s %8.3f %8.3f %8.3f %8.3f %10.1f %6.0f\n",
            "3-factor", fit_3_vals["cfi"], fit_3_vals["tli"],
            fit_3_vals["rmsea"], fit_3_vals["srmr"],
            fit_3_vals["chisq"], fit_3_vals["df"]))
cat(sprintf("%-10s %8.3f %8.3f %8.3f %8.3f %10.1f %6.0f\n",
            "1-factor", fit_1_vals["cfi"], fit_1_vals["tli"],
            fit_1_vals["rmsea"], fit_1_vals["srmr"],
            fit_1_vals["chisq"], fit_1_vals["df"]))
cat("\n")

# Determine best fitting model
best_cfi <- which.max(c(fit_6_vals["cfi"], fit_3_vals["cfi"], fit_1_vals["cfi"]))
model_labels <- c("6-factor", "3-factor", "1-factor")
cat("Best fitting model (highest CFI):", model_labels[best_cfi], "\n\n")

# Check 6-factor thresholds
cfi_6  <- fit_6_vals["cfi"]
tli_6  <- fit_6_vals["tli"]
rmsea_6 <- fit_6_vals["rmsea"]
srmr_6 <- fit_6_vals["srmr"]

cat("6-factor fit assessment:\n")
cat(sprintf("  CFI:   %.3f  (target: >= 0.95)  %s\n", cfi_6,   ifelse(cfi_6 >= 0.95, "PASS", "FAIL")))
cat(sprintf("  TLI:   %.3f  (target: >= 0.95)  %s\n", tli_6,   ifelse(tli_6 >= 0.95, "PASS", "FAIL")))
cat(sprintf("  RMSEA: %.3f  (target: <= 0.06)  %s\n", rmsea_6, ifelse(rmsea_6 <= 0.06, "PASS", "FAIL")))
cat(sprintf("  SRMR:  %.3f  (target: <= 0.08)  %s\n", srmr_6,  ifelse(srmr_6 <= 0.08, "PASS", "FAIL")))
cat("\n")

fit_pass <- (cfi_6 >= 0.95) && (tli_6 >= 0.95) && (rmsea_6 <= 0.06) && (srmr_6 <= 0.08)

# Check 6-factor beats alternatives
six_beats_three <- (fit_6_vals["cfi"] > fit_3_vals["cfi"]) && (fit_6_vals["rmsea"] < fit_3_vals["rmsea"])
six_beats_one   <- (fit_6_vals["cfi"] > fit_1_vals["cfi"]) && (fit_6_vals["rmsea"] < fit_1_vals["rmsea"])

cat(sprintf("6-factor beats 3-factor: %s (CFI diff: %.3f)\n",
            ifelse(six_beats_three, "PASS", "FAIL"),
            fit_6_vals["cfi"] - fit_3_vals["cfi"]))
cat(sprintf("6-factor beats 1-factor: %s (CFI diff: %.3f)\n",
            ifelse(six_beats_one, "PASS", "FAIL"),
            fit_6_vals["cfi"] - fit_1_vals["cfi"]))
cat("\n")

comparison_pass <- six_beats_three && six_beats_one

# --------------------------------------------------------------------------
# Step 8: Chi-square difference test (6-factor vs 3-factor)
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 13.1 (scaled difference test for WLSMV)

cat("================================================================\n")
cat("CHI-SQUARE DIFFERENCE TEST (6-factor vs 3-factor)\n")
cat("================================================================\n\n")

diff_test <- tryCatch({
  anova(fit_6, fit_3)
}, error = function(e) {
  cat("  Note: Scaled difference test via anova().\n")
  NULL
})

if (!is.null(diff_test)) {
  print(diff_test)
  cat("\n")
} else {
  # Manual comparison using chi-square values
  delta_chisq <- fit_3_vals["chisq"] - fit_6_vals["chisq"]
  delta_df <- fit_3_vals["df"] - fit_6_vals["df"]
  if (delta_df > 0) {
    p_val <- pchisq(delta_chisq, df = delta_df, lower.tail = FALSE)
    cat(sprintf("  Delta chi-sq: %.1f, Delta df: %.0f, p: %.4f\n",
                delta_chisq, delta_df, p_val))
    cat(sprintf("  6-factor significantly better: %s\n",
                ifelse(p_val < 0.001, "YES (p < 0.001)", "NO")))
  }
}
cat("\n")

# --------------------------------------------------------------------------
# Step 9: Cronbach's alpha for all 6 subscales
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 11.3 / Section 13.3

cat("================================================================\n")
cat("INTERNAL CONSISTENCY (Cronbach's Alpha)\n")
cat("================================================================\n\n")

subscale_items <- list(
  A_sat   = 1:4,
  A_frust = 5:8,
  B_sat   = 9:12,
  B_frust = 13:16,
  C_sat   = 17:20,
  C_frust = 21:24
)

alpha_results <- numeric(6)
names(alpha_results) <- names(subscale_items)
alpha_all_pass <- TRUE

for (i in seq_along(subscale_items)) {
  sname <- names(subscale_items)[i]
  cols <- subscale_items[[i]]
  a <- psych::alpha(df_numeric[, cols], check.keys = FALSE)$total$raw_alpha
  alpha_results[i] <- a
  status <- ifelse(a >= 0.70, "PASS", "FAIL")
  if (a < 0.70) alpha_all_pass <- FALSE
  cat(sprintf("  %-10s: alpha = %.3f  (target: >= 0.70)  %s\n", sname, a, status))
}
cat("\n")

# --------------------------------------------------------------------------
# Step 10: Factor correlation recovery
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 11.1

cat("================================================================\n")
cat("FACTOR CORRELATION RECOVERY\n")
cat("================================================================\n\n")

cor_est <- lavInspect(fit_6, "cor.lv")

cat(sprintf("%-20s %10s %10s %10s\n", "Factor Pair", "True", "Estimated", "Error"))
cat(paste(rep("-", 55), collapse=""), "\n")

errors <- c()
for (i in 1:(n_factors - 1)) {
  for (j in (i + 1):n_factors) {
    true_val <- cor_matrix[i, j]
    est_val <- cor_est[i, j]
    err <- abs(est_val - true_val)
    errors <- c(errors, err)
    pair_name <- paste(factor_names[i], "<->", factor_names[j])
    cat(sprintf("  %-20s %10.3f %10.3f %10.3f\n", pair_name, true_val, est_val, err))
  }
}

avg_error <- mean(errors)
max_error <- max(errors)
cat(paste(rep("-", 55), collapse=""), "\n")
cat(sprintf("  Average absolute error: %.3f  (target: < 0.05)  %s\n",
            avg_error, ifelse(avg_error < 0.05, "PASS", "FAIL")))
cat(sprintf("  Maximum absolute error: %.3f\n", max_error))
cat("\n")

cor_pass <- avg_error < 0.05

# --------------------------------------------------------------------------
# Step 11: Standardized factor loadings
# --------------------------------------------------------------------------

cat("================================================================\n")
cat("STANDARDIZED FACTOR LOADINGS\n")
cat("================================================================\n\n")

std_solution <- standardizedSolution(fit_6)
loading_rows <- std_solution[std_solution$op == "=~", ]

all_loadings_pass <- TRUE
for (i in 1:nrow(loading_rows)) {
  lhs <- loading_rows$lhs[i]
  rhs <- loading_rows$rhs[i]
  est <- loading_rows$est.std[i]
  status <- ifelse(est >= 0.55, "PASS", "FAIL")
  if (est < 0.55) all_loadings_pass <- FALSE
  cat(sprintf("  %s -> %s: %.3f  %s\n", lhs, rhs, est, status))
}
cat("\n")

# --------------------------------------------------------------------------
# Step 12: Save outputs for audit
# --------------------------------------------------------------------------

# Create output directory if needed
dir.create("outputs/reports", recursive = TRUE, showWarnings = FALSE)

# Save full lavaan summary
sink("outputs/reports/lavaan_full_output.txt")
cat("ABC 6-Factor CFA — Full lavaan Output\n")
cat("Generated:", format(Sys.time()), "\n")
cat("Seed: 42\n")
cat("N:", n_participants, "\n\n")
summary(fit_6, fit.measures = TRUE, standardized = TRUE, rsquare = TRUE)
sink()

# Save model comparison CSV
compare_df <- data.frame(
  Model = c("6-factor", "3-factor", "1-factor"),
  CFI = c(fit_6_vals["cfi"], fit_3_vals["cfi"], fit_1_vals["cfi"]),
  TLI = c(fit_6_vals["tli"], fit_3_vals["tli"], fit_1_vals["tli"]),
  RMSEA = c(fit_6_vals["rmsea"], fit_3_vals["rmsea"], fit_1_vals["rmsea"]),
  SRMR = c(fit_6_vals["srmr"], fit_3_vals["srmr"], fit_1_vals["srmr"]),
  ChiSq = c(fit_6_vals["chisq"], fit_3_vals["chisq"], fit_1_vals["chisq"]),
  df = c(fit_6_vals["df"], fit_3_vals["df"], fit_1_vals["df"])
)
write.csv(compare_df, "outputs/reports/model_comparison.csv", row.names = FALSE)

# Save correlation recovery CSV
cor_pairs <- c()
cor_true <- c()
cor_estimated <- c()
cor_errors <- c()
for (i in 1:(n_factors - 1)) {
  for (j in (i + 1):n_factors) {
    cor_pairs <- c(cor_pairs, paste(factor_names[i], "<->", factor_names[j]))
    cor_true <- c(cor_true, cor_matrix[i, j])
    cor_estimated <- c(cor_estimated, cor_est[i, j])
    cor_errors <- c(cor_errors, abs(cor_est[i, j] - cor_matrix[i, j]))
  }
}
cor_recovery_df <- data.frame(
  Factor_Pair = cor_pairs,
  True = cor_true,
  Estimated = cor_estimated,
  Absolute_Error = cor_errors
)
write.csv(cor_recovery_df, "outputs/reports/correlation_recovery.csv", row.names = FALSE)

# Save reliability CSV
reliability_df <- data.frame(
  Subscale = names(alpha_results),
  Cronbach_Alpha = round(as.numeric(alpha_results), 3),
  Pass = alpha_results >= 0.70
)
write.csv(reliability_df, "outputs/reports/reliability_analysis.csv", row.names = FALSE)

# Save model object
saveRDS(fit_6, "outputs/reports/lavaan_model_6factor.rds")

cat("Audit outputs saved to outputs/reports/:\n")
cat("  lavaan_full_output.txt\n")
cat("  model_comparison.csv\n")
cat("  correlation_recovery.csv\n")
cat("  reliability_analysis.csv\n")
cat("  lavaan_model_6factor.rds\n\n")

# --------------------------------------------------------------------------
# Step 13: Final verdict
# --------------------------------------------------------------------------

cat("================================================================\n")
cat("FINAL VALIDATION VERDICT\n")
cat("================================================================\n\n")

checks <- data.frame(
  Check = c(
    "6-factor CFA fit (CFI >= 0.95, RMSEA <= 0.06)",
    "6-factor beats 3-factor",
    "6-factor beats 1-factor",
    "All Cronbach alphas >= 0.70",
    "Correlation recovery error < 0.05",
    "All loadings >= 0.55"
  ),
  Result = c(
    ifelse(fit_pass, "PASS", "FAIL"),
    ifelse(six_beats_three, "PASS", "FAIL"),
    ifelse(six_beats_one, "PASS", "FAIL"),
    ifelse(alpha_all_pass, "PASS", "FAIL"),
    ifelse(cor_pass, "PASS", "FAIL"),
    ifelse(all_loadings_pass, "PASS", "FAIL")
  )
)

for (i in 1:nrow(checks)) {
  cat(sprintf("  [%s] %s\n", checks$Result[i], checks$Check[i]))
}
cat("\n")

all_pass <- fit_pass && comparison_pass && alpha_all_pass && cor_pass && all_loadings_pass

if (all_pass) {
  cat("  ABC 6-FACTOR MODEL VALIDATED\n\n")
  cat("  The satisfaction/frustration split is empirically supported.\n")
  cat("  Proceed to Python production implementation.\n")
} else {
  cat("  VALIDATION FAILED\n\n")
  cat("  DO NOT proceed to Python implementation.\n")
  cat("  Review failed checks above and consult spec.\n")
}
cat("\n================================================================\n")
