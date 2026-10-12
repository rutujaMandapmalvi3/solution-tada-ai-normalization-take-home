# Tada AI · Data Normalization — Solution

## Problem Statement

Build a local platform that normalizes company, employee, direct deposit, deduction, and payroll data from
**PrismHR, isolved, and UKG Ready** into a consistent model. Discover the provider
mappings, design your own canonical schemas and enums, generate synthetic test
data, and implement transformations that preserve the meaning of the source data.
Use any programming language or stack.
You can use AI as much as you want throughout this project.

## Problem Breakdown
<!-- Steps followed to solve it -->

1. **Access Provider Data**: Sign in to PrismHR, isolved, and UKG Ready, then fetch company, employee, direct deposit, deduction, and payroll data.
2. **Discover Mappings**: Match each provider's fields and codes to one another using the specs, the lookup files, and the live data.
3. **Design Canonical Schemas & Enums**: Define one standard model for Company, Employee, Direct Deposit, Deductions, and Payroll, with standard codes and company → employee links.
4. **Generate Fixtures**: Create deterministic synthetic provider data for testing.
5. **Transform**: Convert each provider's data into the canonical model without changing its meaning.
6. **Test**: Verify the transformations offline using the fixtures.
7. **Optional: Write to Provider**: Map canonical employee data back into a provider's format and create or update the employee there.

### 1. Access Provider Data
<!-- Sign-in, auth, endpoints used per provider -->

### 2. Discover Mappings
<!-- How provider fields/codes were matched -->

### 3. Design Canonical Schemas & Enums
<!-- Company, Employee, Direct Deposit, Deductions, Payroll; standard codes; how records link -->

### 4. Generate Fixtures
<!-- Deterministic synthetic test data -->

### 5. Transform
<!-- Provider data → canonical model -->

### 6. Test
<!-- How correctness is verified, offline -->

### 7. Optional: Write to Provider
<!-- Whether/how built -->

## Setup
<!-- Prerequisites, install, env vars (never real secrets) -->

## Usage
<!-- Commands: normalize, generate fixtures, run tests -->

## Architecture
<!-- Components and data flow -->

## Project Structure
<!-- Folder layout -->

## Limitations
<!-- What isn't covered -->
