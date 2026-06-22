from sqlalchemy import select, and_, func
import scipy.stats as stats
import numpy as np
from uuid import UUID
from app.models.experiment import Assignment, Experiment, Event, Result
from app.constants import CONTROL, TREATMENT, CONFIDENCE_THRESHOLD, INCONCLUSIVE, INSUFFICIENT_DATA

# Runs the whole process for the stats engine
def run_stats_engine(experiment_id: UUID, db_session):
    # count total assignments per variants & matching events per variant
    total_assignments = count_assignments(experiment_id, db_session)
    total_conversions = count_conversions_per_variant(experiment_id, db_session)
    # get experiment's result
    result = get_results(experiment_id, total_assignments, total_conversions, db_session)
    return result

# Count total assignments per variants (control vs. treatment)
def count_assignments(experiment_id, db_session):
    total_count = dict()
    total_count[CONTROL] = db_session.scalars(
        select(func.count()).select_from(Assignment).where(and_(
            Assignment.experiment_id == experiment_id,
            Assignment.variant == CONTROL
    ))).first()
    total_count[TREATMENT] = db_session.scalars(
        select(func.count()).select_from(Assignment).where(and_(
            Assignment.experiment_id == experiment_id,
            Assignment.variant == TREATMENT
    ))).first()
    return total_count

# Count total matching events per variant (conversions)
def count_conversions_per_variant(experiment_id, db_session):
    # store the counts -- to be returned
    total_count = dict()
    # fetch the success metric for the experiment
    success_metric = db_session.scalars(
        select(Experiment.success_metric).where(Experiment.id == experiment_id)).first()
    # count conversions per variant (control vs. treatment)
    for assignment in [CONTROL, TREATMENT]:
        nested = select(Assignment.session_id).where(and_(
            Assignment.experiment_id == experiment_id,
            Assignment.variant == assignment
        ))
        statement = select(func.count()).select_from(Event).where(and_(
            Event.experiment_id == experiment_id,
            Event.event_type == success_metric,
            Event.session_id.in_(nested)
        ))
        total_count[assignment] = db_session.scalars(statement).first()
    return total_count

# Calculate & update values for the experiment results table
def get_results(experiment_id, assignment_counts, conversion_counts, db_session):
    # Check if it exceeds minimum threshold
    if not (assignment_counts[CONTROL] > 0 and assignment_counts[TREATMENT] > 0):
        new_result = dict(
            experiment_id=experiment_id,
            control_conversions=conversion_counts[CONTROL],
            treatment_conversions=conversion_counts[TREATMENT],
            control_rate=None,
            treatment_rate=None,
            lift=None,
            confidence=None,
            winner=INSUFFICIENT_DATA
        )
    else:
        # calculate control & treatment rate
        control_rate, treatment_rate = calculate_rates(assignment_counts, conversion_counts)
        # calculate lift
        lift = calculate_lift(treatment_rate, control_rate)
        # perform chi-square test
        _, p_value, _, _ = perform_chi_square_test(assignment_counts, conversion_counts)
        # calculate statistical confidence
        confidence = round(float((1 - p_value) * 100), 3)
        # determine winner
        winner = determine_winner(confidence, treatment_rate, control_rate)
        # insert result into the database
        new_result = dict(
            experiment_id=experiment_id,
            control_conversions=conversion_counts[CONTROL],
            treatment_conversions=conversion_counts[TREATMENT],
            control_rate=control_rate,
            treatment_rate=treatment_rate,
            lift=lift,
            confidence=confidence,
            winner=winner
        )
    return new_result

# Calculate control & treatment rates
def calculate_rates(assignment_counts, conversion_counts):
    control_rate = round((conversion_counts[CONTROL] / assignment_counts[CONTROL]), 3)
    treatment_rate = round((conversion_counts[TREATMENT] / assignment_counts[TREATMENT]), 3)
    return control_rate, treatment_rate

# Calculate lift (percentage improvement)
def calculate_lift(treatment_rate, control_rate):
    if control_rate == 0:
        return None
    lift = round(((treatment_rate - control_rate) / control_rate), 3)
    return lift

# Perform chi square test 
def perform_chi_square_test(assignment_counts, conversion_counts):
    # Initialize variables with values
    treatment_total = assignment_counts[TREATMENT]
    treatment_success = conversion_counts[TREATMENT]
    treatment_failure = treatment_total - treatment_success
    control_total = assignment_counts[CONTROL]
    control_success = conversion_counts[CONTROL]
    control_failure = control_total - control_success
    # Build the 2x2 contingency table
    table = np.array([
        [treatment_success, treatment_failure],
        [control_success, control_failure]
    ])
    # Run chi-square test
    chi2, p_value, dof, expected = stats.chi2_contingency(table, correction=True)
    return chi2, p_value, dof, expected

# Determine winner based on previous calculations
def determine_winner(confidence, treatment_rate, control_rate):
    if confidence >= CONFIDENCE_THRESHOLD:
        if treatment_rate > control_rate:
            winner = TREATMENT
        elif treatment_rate < control_rate:
            winner= CONTROL
        else:
            winner = INCONCLUSIVE
    else:
        winner = INCONCLUSIVE
    return winner