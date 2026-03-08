# ============================================================================
# 01_simple_cfa_test.R
# Simple 2-factor CFA: A-sat and A-frust only
# Purpose: Validate R/lavaan environment before building full 6-factor model
#
# Reference: abc-assessment-spec Section 11.1 (latent structure)
# Reference: abc-assessment-spec Section 13.1 (CFA methodology)
# Reference: abc-assessment-spec Section 11.3 (fit thresholds)
# ============================================================================

library(lavaan)
library(MASS)
library(psych)

set.seed(42)  # Rule 7: Reproducibility

cat("\n")
cat("========================================\n")
cat("  SIMPLE 2-FACTOR CFA VALIDATION TEST  \n")
cat("========================================\n\n")

# --------------------------------------------------------------------------
# Step 1: Define population parameters
# --------------------------------------------------------------------------
# Two factors: A-sat and A-frust
# Within-domain correlation: r = -0.50
# Reference: abc-assessment-spec Section 11.1 (within-domain sat/frust: -0.40 to -0.60)

n_participants <- 1000
n_items_per_factor <- 4
true_correlation <- -0.50

# Factor loading targets: 0.60 - 0.80
# Reference: abc-assessment-spec Section 13.1 (target loadings)
loadings_a_sat <- c(0.75, 0.70, 0.72, 0.68)    # 4 items for A-sat
loadings_a_frust <- c(0.73, 0.71, 0.69, 0.74)   # 4 items for A-frust

cat("Population parameters:\n")
cat("  N participants:", n_participants, "\n")
cat("  True A-sat <-> A-frust correlation:", true_correlation, "\n")
cat("  A-sat loadings:", paste(loadings_a_sat, collapse=", "), "\n")
cat("  A-frust loadings:", paste(loadings_a_frust, collapse=", "), "\n\n")

# --------------------------------------------------------------------------
# Step 2: Build factor loading matrix and generate data
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 13.1
# Sigma = Lambda * Phi * Lambda' + Theta

# Loading matrix (8 items x 2 factors)
Lambda <- matrix(0, nrow = 8, ncol = 2)
Lambda[1:4, 1] <- loadings_a_sat      # Items 1-4 load on A-sat
Lambda[5:8, 2] <- loadings_a_frust    # Items 5-8 load on A-frust

# Factor correlation matrix (Phi)
Phi <- matrix(c(
  1.00, true_correlation,
  true_correlation, 1.00
), nrow = 2)

# Unique variances (Theta): 1 - loading^2 for each item
diag_theta <- 1 - diag(Lambda %*% t(Lambda))
# Ensure positive unique variances
diag_theta <- pmax(diag_theta, 0.10)
Theta <- diag(diag_theta)

# Model-implied covariance matrix
Sigma <- Lambda %*% Phi %*% t(Lambda) + Theta

cat("Model-implied covariance matrix constructed.\n")
cat("  Matrix is positive definite:", all(eigen(Sigma)$values > 0), "\n\n")

# --------------------------------------------------------------------------
# Step 3: Generate multivariate normal data and discretize to 1-7 Likert
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 11.2 (synthetic response generation)
# Reference: abc-assessment-spec Section 13.1 (ordinal discretisation)

# Draw continuous data
continuous_data <- mvrnorm(n = n_participants, mu = rep(0, 8), Sigma = Sigma)

# Discretize to 1-7 scale using threshold-based mapping
# Thresholds calibrated for realistic distributions
# Slight positive skew for satisfaction, slight negative skew for frustration
thresholds_sat <- c(-2.0, -1.2, -0.4, 0.4, 1.2, 2.0)
thresholds_frust <- c(-2.0, -1.2, -0.4, 0.4, 1.2, 2.0)

discretize <- function(x, thresholds) {
  result <- rep(1L, length(x))
  for (k in seq_along(thresholds)) {
    result <- result + as.integer(x > thresholds[k])
  }
  return(result)
}

# Apply discretization
ordinal_data <- matrix(0L, nrow = n_participants, ncol = 8)
for (j in 1:4) {
  ordinal_data[, j] <- discretize(continuous_data[, j], thresholds_sat)
}
for (j in 5:8) {
  ordinal_data[, j] <- discretize(continuous_data[, j], thresholds_frust)
}

# Create data frame with named columns
df <- as.data.frame(ordinal_data)
colnames(df) <- c("AS1", "AS2", "AS3", "AS4", "AF1", "AF2", "AF3", "AF4")

# Convert to ordered factors (required for WLSMV)
for (col in names(df)) {
  df[[col]] <- ordered(df[[col]])
}

cat("Data generation complete.\n")
cat("  Dimensions:", nrow(df), "x", ncol(df), "\n")
cat("  Response range: 1 to 7\n")
cat("  Sample means (A-sat items):", paste(round(sapply(df[,1:4], function(x) mean(as.numeric(x))), 2), collapse=", "), "\n")
cat("  Sample means (A-frust items):", paste(round(sapply(df[,5:8], function(x) mean(as.numeric(x))), 2), collapse=", "), "\n\n")

# --------------------------------------------------------------------------
# Step 4: Define and fit 2-factor CFA model
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 13.1 (CFA specification)
# Estimator: WLSMV for ordinal data
# Reference: abc-assessment-spec Section 13.1 (WLSMV justification)

model_2factor <- '
  # Factor definitions
  A_sat   =~ AS1 + AS2 + AS3 + AS4
  A_frust =~ AF1 + AF2 + AF3 + AF4

  # Factor correlation (estimated freely)
  A_sat ~~ A_frust
'

cat("Fitting 2-factor CFA model (WLSMV estimator)...\n")

fit_2factor <- cfa(
  model_2factor,
  data = df,
  ordered = TRUE,           # Treat as ordinal
  estimator = "WLSMV"       # Gold-standard for ordinal CFA
)

cat("  Model converged:", lavInspect(fit_2factor, "converged"), "\n\n")

# --------------------------------------------------------------------------
# Step 5: Extract and evaluate fit indices
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 11.3 / Section 13.1 (fit thresholds)
# Gold standard: CFI >= 0.95, TLI >= 0.95, RMSEA <= 0.06, SRMR <= 0.08

fit_measures <- fitMeasures(fit_2factor, c("cfi", "tli", "rmsea", "srmr"))

cfi  <- fit_measures["cfi"]
tli  <- fit_measures["tli"]
rmsea <- fit_measures["rmsea"]
srmr <- fit_measures["srmr"]

cat("========================================\n")
cat("FIT INDICES:\n")
cat("========================================\n")
cat(sprintf("  CFI:   %.3f  (target: >= 0.95)  %s\n", cfi,   ifelse(cfi >= 0.95, "PASS", "FAIL")))
cat(sprintf("  TLI:   %.3f  (target: >= 0.95)  %s\n", tli,   ifelse(tli >= 0.95, "PASS", "FAIL")))
cat(sprintf("  RMSEA: %.3f  (target: <= 0.06)  %s\n", rmsea, ifelse(rmsea <= 0.06, "PASS", "FAIL")))
cat(sprintf("  SRMR:  %.3f  (target: <= 0.08)  %s\n", srmr,  ifelse(srmr <= 0.08, "PASS", "FAIL")))
cat("========================================\n\n")

fit_pass <- (cfi >= 0.95) && (tli >= 0.95) && (rmsea <= 0.06) && (srmr <= 0.08)

if (fit_pass) {
  cat("MODEL PASSES all fit thresholds.\n\n")
} else {
  cat("MODEL FAILS one or more fit thresholds.\n\n")
}

# --------------------------------------------------------------------------
# Step 6: Extract factor correlation and check recovery
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 11.1 (correlation recovery)

cor_est <- lavInspect(fit_2factor, "cor.lv")
estimated_cor <- cor_est["A_sat", "A_frust"]
recovery_error <- abs(estimated_cor - true_correlation)

cat("========================================\n")
cat("CORRELATION RECOVERY:\n")
cat("========================================\n")
cat(sprintf("  Estimated A-sat <-> A-frust: %.3f\n", estimated_cor))
cat(sprintf("  True population correlation: %.3f\n", true_correlation))
cat(sprintf("  Recovery error:              %.3f  (target: < 0.05)  %s\n",
            recovery_error, ifelse(recovery_error < 0.05, "PASS", "FAIL")))
cat("========================================\n\n")

cor_pass <- recovery_error < 0.05

# --------------------------------------------------------------------------
# Step 7: Cronbach's alpha for both subscales
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 11.3 / Section 13.3 (internal consistency)

# Convert back to numeric for psych::alpha
df_numeric <- as.data.frame(lapply(df, function(x) as.numeric(x)))

alpha_a_sat <- psych::alpha(df_numeric[, 1:4], check.keys = FALSE)$total$raw_alpha
alpha_a_frust <- psych::alpha(df_numeric[, 5:8], check.keys = FALSE)$total$raw_alpha

cat("========================================\n")
cat("INTERNAL CONSISTENCY:\n")
cat("========================================\n")
cat(sprintf("  A-sat  alpha: %.3f  (target: >= 0.70)  %s\n",
            alpha_a_sat, ifelse(alpha_a_sat >= 0.70, "PASS", "FAIL")))
cat(sprintf("  A-frust alpha: %.3f  (target: >= 0.70)  %s\n",
            alpha_a_frust, ifelse(alpha_a_frust >= 0.70, "PASS", "FAIL")))
cat("========================================\n\n")

alpha_pass <- (alpha_a_sat >= 0.70) && (alpha_a_frust >= 0.70)

# --------------------------------------------------------------------------
# Step 8: Standardized factor loadings
# --------------------------------------------------------------------------

cat("========================================\n")
cat("STANDARDIZED FACTOR LOADINGS:\n")
cat("========================================\n")

std_est <- standardizedSolution(fit_2factor)
loadings_table <- std_est[std_est$op == "=~", c("lhs", "rhs", "est.std")]

for (i in 1:nrow(loadings_table)) {
  loading <- loadings_table$est.std[i]
  status <- ifelse(loading >= 0.55, "PASS", "FAIL")
  cat(sprintf("  %s -> %s: %.3f  (target: >= 0.55)  %s\n",
              loadings_table$lhs[i], loadings_table$rhs[i], loading, status))
}
cat("========================================\n\n")

# --------------------------------------------------------------------------
# Step 9: Final verdict
# --------------------------------------------------------------------------

all_pass <- fit_pass && cor_pass && alpha_pass

cat("========================================\n")
cat("FINAL VERDICT:\n")
cat("========================================\n")
if (all_pass) {
  cat("\n  SIMPLE 2-FACTOR CFA TEST PASSED\n\n")
  cat("  Fit indices: PASS\n")
  cat("  Correlation recovery: PASS\n")
  cat("  Internal consistency: PASS\n")
  cat("\n  R/lavaan environment validated.\n")
  cat("  Ready to proceed to full 6-factor model.\n")
} else {
  cat("\n  SIMPLE 2-FACTOR CFA TEST FAILED\n\n")
  cat(sprintf("  Fit indices: %s\n", ifelse(fit_pass, "PASS", "FAIL")))
  cat(sprintf("  Correlation recovery: %s\n", ifelse(cor_pass, "PASS", "FAIL")))
  cat(sprintf("  Internal consistency: %s\n", ifelse(alpha_pass, "PASS", "FAIL")))
  cat("\n  DO NOT proceed to 6-factor model. Debug first.\n")
}
cat("========================================\n")
