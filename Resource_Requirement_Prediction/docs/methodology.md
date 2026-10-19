# Research Methodology

## 1. Research Approach

This research develops an AI-driven framework for predicting road maintenance resource requirements and optimizing the allocation of available resources. The proposed system combines data preparation, machine-learning prediction, resource availability checking, and multi-objective optimization.

## 2. Data Sources

The available data includes a forecasted routine maintenance budget workbook containing 123 records across six road identifiers and 25 maintenance item codes. The workbook contains maintenance quantities, units, rates, chainage information, measurement fields, and maintenance frequency.

Additional road traffic, weather, and road survey datasets may be investigated for use as prediction features, subject to data quality, relevance, and compatibility checks.

The inspection dates in the budget workbook range from February to March 2025. Their interpretation and relationship to the 2026 forecast budget must be confirmed before modelling.

## 3. Data Preparation

The data preparation stage will:
- Inspect column names, data types, units, and missing values.
- Check duplicate records and inconsistent measurements.
- Investigate the meaning of maintenance item codes.
- Verify date formats and the meaning of date fields.
- Separate genuine missing values from zero values.
- Record the source and status of each dataset.

Data will not be treated as actual resource consumption unless the source supports that interpretation.

## 4. Resource Requirement Prediction

A machine-learning model will be developed after a suitable prediction target and relevant input features have been established.

The available maintenance quantity data will first be assessed for its suitability as a prediction target. Additional verified data may be required to predict labour and equipment requirements directly.

A simple baseline will be established before evaluating a machine-learning model. The evaluation method and metrics will be selected according to the target variable and the amount and structure of the available data.

## 5. Resource Availability

The framework will check predicted resource requirements against available resource quantities when reliable availability data is obtained.

If real availability data is unavailable, example availability values may be used for a clearly labelled demonstration. Such values will be identified as simulated and will not be presented as actual RDA stock or capacity.

## 6. Resource Allocation Optimization

The proposed optimization stage will investigate the use of NSGA-II for multi-objective resource allocation.

The objectives and constraints will be defined using verified data and documented assumptions. Potential considerations include resource utilization, unmet requirements, maintenance coverage, and allocation feasibility.

The optimization results will be compared with a simple baseline allocation method. Simulated inputs and results will be clearly distinguished from actual records.

## 7. System Development

The planned system will contain:
- A React frontend for entering maintenance details and displaying predictions and allocation results.
- A Python FastAPI backend for data validation and communication with the prediction and optimization modules.
- Data-processing and machine-learning components implemented in Python.
- A data storage approach selected according to the prototype's requirements.

The frontend and backend will be integrated after the prediction and allocation components have been tested independently.

## 8. Evaluation

The prediction component will be evaluated using an appropriate test strategy and suitable metrics, selected after the prediction target is confirmed.

The allocation component will be evaluated using defined measures such as resource utilization, unmet requirements, maintenance coverage, and constraint satisfaction, where the required data supports these calculations.

The framework's limitations, data gaps, assumptions, and the distinction between actual, estimated, and simulated values will be documented.

## 9. Research Integrity

Only verified source data will be described as actual. Model-generated values will be described as predictions or estimates, and artificially created demonstration inputs will be labelled as simulated.

No model accuracy, resource savings, or operational improvement will be claimed before the corresponding evaluation has been performed.
