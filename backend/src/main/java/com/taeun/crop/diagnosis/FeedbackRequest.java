package com.taeun.crop.diagnosis;

import jakarta.validation.constraints.NotNull;

public record FeedbackRequest(@NotNull Feedback feedback) {
}
