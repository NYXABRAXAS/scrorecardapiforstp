from app.core.enums import BureauRisk


class BureauRiskClassifier:
    def classify(self, context: dict) -> BureauRisk:
        max_dpd = context.get("maxDPD") or 0
        dpd60 = context.get("dpd60Count") or 0
        dpd90 = context.get("dpd90Count") or 0
        enquiries = context.get("creditEnquiries6M") or 0
        unsecured = context.get("activeUnsecuredLoans") or 0
        cibil = context.get("cibilScore") or 0
        overdue = context.get("overdueAmount") or 0
        dpd30 = context.get("dpd30Count") or 0

        if dpd60 > 0 or dpd90 > 0 or max_dpd > 90 or enquiries > 5 or unsecured > 2:
            return BureauRisk.HIGH
        if dpd30 > 0 or max_dpd > 0 or enquiries > 2 or 700 <= cibil <= 750:
            return BureauRisk.MEDIUM
        if cibil > 750 and overdue <= 0 and enquiries <= 2:
            return BureauRisk.LOW
        return BureauRisk.MEDIUM

