# ============================================================================
# 03_export_ground_truth.R
# Generate synthetic response data with known latent scores for Python validation
#
# Exports:
#   outputs/datasets/ground_truth_responses.csv  (raw 1-7 item responses)
#   outputs/datasets/ground_truth_latent.csv     (true latent factor scores)
#   outputs/datasets/ground_truth_states.csv     (true domain states)
#
# Reference: abc-assessment-spec Section 11.2 (synthetic response generation)
# Reference: abc-assessment-spec Section 11.4 (scoring pipeline verification)
# ============================================================================

library(MASS)

set.seed(42)  # Rule 7: Reproducibility

cat("\n")
cat("================================================================\n")
cat("  GENERATING GROUND TRUTH DATA FOR PYTHON VALIDATION\n")
cat("================================================================\n\n")

# --------------------------------------------------------------------------
# Step 1: Population parameters (same as 02_abc_6factor_cfa.R)
# --------------------------------------------------------------------------

n_participants <- 1000
factor_names <- c("a_sat", "a_frust", "b_sat", "b_frust", "c_sat", "c_frust")

cor_matrix <- matrix(c(
   1.00, -0.50,  0.30, -0.15,  0.35, -0.10,
  -0.50,  1.00, -0.15,  0.35, -0.10,  0.40,
   0.30, -0.15,  1.00, -0.55,  0.25, -0.20,
  -0.15,  0.35, -0.55,  1.00, -0.10,  0.35,
   0.35, -0.10,  0.25, -0.10,  1.00, -0.45,
  -0.10,  0.40, -0.20,  0.35, -0.45,  1.00
), nrow = 6, byrow = TRUE)

# --------------------------------------------------------------------------
# Step 2: Loading matrix (same as 02_abc_6factor_cfa.R)
# --------------------------------------------------------------------------

Lambda <- matrix(0, nrow = 24, ncol = 6)
Lambda[1, 1] <- 0.75; Lambda[2, 1] <- 0.72; Lambda[3, 1] <- 0.70; Lambda[4, 1] <- 0.65
Lambda[5, 2] <- 0.74; Lambda[6, 2] <- 0.71; Lambda[7, 2] <- 0.73; Lambda[8, 2] <- 0.66
Lambda[9, 3] <- 0.73; Lambda[10, 3] <- 0.70; Lambda[11, 3] <- 0.68; Lambda[12, 3] <- 0.64
Lambda[13, 4] <- 0.76; Lambda[14, 4] <- 0.72; Lambda[15, 4] <- 0.69; Lambda[16, 4] <- 0.67
Lambda[17, 5] <- 0.74; Lambda[18, 5] <- 0.71; Lambda[19, 5] <- 0.73; Lambda[20, 5] <- 0.63
Lambda[21, 6] <- 0.75; Lambda[22, 6] <- 0.70; Lambda[23, 6] <- 0.72; Lambda[24, 6] <- 0.65

# --------------------------------------------------------------------------
# Step 3: Generate latent factor scores
# --------------------------------------------------------------------------
# Draw from multivariate normal with the specified correlations

latent_scores <- mvrnorm(n = n_participants, mu = rep(0, 6), Sigma = cor_matrix)
colnames(latent_scores) <- factor_names

cat("Generated", n_participants, "latent score vectors.\n")

# --------------------------------------------------------------------------
# Step 4: Generate observed items from latent scores
# --------------------------------------------------------------------------
# x_ij = lambda_j * eta_i + epsilon_ij
# Reference: abc-assessment-spec Section 13.1

Sigma_model <- Lambda %*% cor_matrix %*% t(Lambda)
diag_unique <- 1 - diag(Sigma_model)
diag_unique <- pmax(diag_unique, 0.15)

continuous_items <- matrix(0, nrow = n_participants, ncol = 24)
for (j in 1:24) {
  factor_idx <- which(Lambda[j, ] != 0)
  loading <- Lambda[j, factor_idx]
  unique_sd <- sqrt(diag_unique[j])
  continuous_items[, j] <- loading * latent_scores[, factor_idx] + rnorm(n_participants, 0, unique_sd)
}

# --------------------------------------------------------------------------
# Step 5: Discretize to 1-7 Likert
# --------------------------------------------------------------------------

thresholds <- c(-2.0, -1.2, -0.4, 0.4, 1.2, 2.0)

discretize <- function(x, thresh) {
  result <- rep(1L, length(x))
  for (k in seq_along(thresh)) {
    result <- result + as.integer(x > thresh[k])
  }
  return(result)
}

ordinal_items <- matrix(0L, nrow = n_participants, ncol = 24)
for (j in 1:24) {
  ordinal_items[, j] <- discretize(continuous_items[, j], thresholds)
}

item_names <- c(
  paste0("AS", 1:4), paste0("AF", 1:4),
  paste0("BS", 1:4), paste0("BF", 1:4),
  paste0("CS", 1:4), paste0("CF", 1:4)
)
colnames(ordinal_items) <- item_names

cat("Discretized to 1-7 Likert scale.\n")

# --------------------------------------------------------------------------
# Step 6: Compute subscale scores from observed items (same algorithm as Python)
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 2.1, Section 13.2
# Algorithm: reverse-score item 4 of each subscale (8 - r),
#            compute 4-item mean, normalize ((mean - 1) / 6) * 10

# Reverse-score item 4 of each subscale
reverse_items <- c("AS4", "AF4", "BS4", "BF4", "CS4", "CF4")
scored_items <- ordinal_items
for (item in reverse_items) {
  scored_items[, item] <- 8L - scored_items[, item]
}

cat("Applied reverse scoring to item 4 of each subscale.\n")

# Compute subscale means and normalize to 0-10
subscale_map <- list(
  a_sat   = c("AS1", "AS2", "AS3", "AS4"),
  a_frust = c("AF1", "AF2", "AF3", "AF4"),
  b_sat   = c("BS1", "BS2", "BS3", "BS4"),
  b_frust = c("BF1", "BF2", "BF3", "BF4"),
  c_sat   = c("CS1", "CS2", "CS3", "CS4"),
  c_frust = c("CF1", "CF2", "CF3", "CF4")
)

observed_subscales <- matrix(0, nrow = n_participants, ncol = 6)
colnames(observed_subscales) <- factor_names

for (s in seq_along(subscale_map)) {
  sub_name <- names(subscale_map)[s]
  items <- subscale_map[[s]]
  raw_mean <- rowMeans(scored_items[, items])
  observed_subscales[, sub_name] <- ((raw_mean - 1.0) / 6.0) * 10.0
}

cat("Computed observed subscale scores (0-10 scale).\n")

# Also export the latent scores mapped to 0-10 for reference
map_latent_to_10 <- function(z) {
  likert_mean <- 4.0 + z * 1.5
  likert_mean <- pmax(1.0, pmin(7.0, likert_mean))
  normalized <- ((likert_mean - 1.0) / 6.0) * 10.0
  return(normalized)
}

latent_normalized <- apply(latent_scores, 2, map_latent_to_10)
colnames(latent_normalized) <- factor_names

# --------------------------------------------------------------------------
# Step 7: Compute domain states from observed subscale scores
# --------------------------------------------------------------------------
# Reference: abc-assessment-spec Section 2.2

classify_state <- function(sat, frust) {
  ifelse(sat >= 5.5 & frust < 5.5, "Thriving",
  ifelse(sat >= 5.5 & frust >= 5.5, "Vulnerable",
  ifelse(sat < 5.5 & frust < 5.5, "Mild",
         "Distressed")))
}

states <- data.frame(
  ambition = classify_state(observed_subscales[, "a_sat"], observed_subscales[, "a_frust"]),
  belonging = classify_state(observed_subscales[, "b_sat"], observed_subscales[, "b_frust"]),
  craft = classify_state(observed_subscales[, "c_sat"], observed_subscales[, "c_frust"])
)

cat("Computed true domain states.\n\n")

# --------------------------------------------------------------------------
# Step 8: Export CSVs
# --------------------------------------------------------------------------

dir.create("outputs/datasets", recursive = TRUE, showWarnings = FALSE)

write.csv(as.data.frame(ordinal_items), "outputs/datasets/ground_truth_responses.csv",
          row.names = FALSE)
write.csv(as.data.frame(observed_subscales), "outputs/datasets/ground_truth_subscales.csv",
          row.names = FALSE)
write.csv(as.data.frame(latent_normalized), "outputs/datasets/ground_truth_latent.csv",
          row.names = FALSE)
write.csv(states, "outputs/datasets/ground_truth_states.csv",
          row.names = FALSE)

cat("Exported:\n")
cat("  outputs/datasets/ground_truth_responses.csv  (", n_participants, "x 24)\n")
cat("  outputs/datasets/ground_truth_subscales.csv  (", n_participants, "x 6)\n")
cat("  outputs/datasets/ground_truth_latent.csv     (", n_participants, "x 6)\n")
cat("  outputs/datasets/ground_truth_states.csv     (", n_participants, "x 3)\n\n")

# Quick summary
cat("State distribution:\n")
for (domain in c("ambition", "belonging", "craft")) {
  cat("  ", domain, ":\n")
  tbl <- table(states[[domain]])
  for (s in names(tbl)) {
    cat("    ", s, ":", tbl[s], sprintf("(%.1f%%)", 100 * tbl[s] / n_participants), "\n")
  }
}

cat("\n================================================================\n")
cat("  GROUND TRUTH DATA EXPORTED\n")
cat("================================================================\n")
