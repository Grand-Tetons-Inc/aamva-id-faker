# SOLID REFACTORING MASTER PLAN
## AAMVA ID Faker - Complete Architectural Transformation

**Plan Generated:** 2025-11-20
**Branch:** claude/plan-solid-refactor-018N2uob8mV8j6Z1nFb1E5Ze
**Multi-Agent Analysis:** 10 specialized agents
**Total Analysis:** 4,674 lines of code reviewed

---

## EXECUTIVE SUMMARY

This master plan represents the consolidated findings of 10 specialized AI agents who analyzed the AAMVA ID Faker project from different perspectives. After thorough analysis and "debate" among agents, we have reached **consensus** on the optimal refactoring strategy to transform this 786-line procedural script into a professional, SOLID-compliant Python library.

### Critical Consensus Points

**All 10 agents agree:**
1. ✅ Current code is **functionally correct** but architecturally flawed
2. ✅ **SOLID principles are heavily violated** throughout
3. ✅ Refactoring is **essential** for maintainability, testability, and extensibility
4. ✅ **Incremental refactoring** is safer than big-bang rewrite
5. ✅ Documentation quality is excellent (9/10) - rare for codebase this size
6. ✅ No inheritance exists (good!) - easier to refactor
7. ✅ **Testability is critical** - current code cannot be tested (2/10)

### Severity Assessment (Agent Consensus)

| Dimension | Current Score | Target Score | Priority |
|-----------|--------------|--------------|----------|
| **SOLID Compliance** | 2/10 | 9/10 | 🔴 CRITICAL |
| **Testability** | 2/10 | 9/10 | 🔴 CRITICAL |
| **Error Handling** | 2/10 | 9/10 | 🔴 CRITICAL |
| **Code Duplication** | 5/10 (25-30%) | 9/10 (<5%) | 🟠 HIGH |
| **Extensibility** | 2/10 | 9/10 | 🟠 HIGH |
| **Type Safety** | 1/10 | 9/10 | 🟠 HIGH |
| **Documentation** | 9/10 | 9.5/10 | 🟢 LOW |
| **Functionality** | 8/10 | 9/10 | 🟢 LOW |

---

## AGENT DEBATES & CONSENSUS

### Debate 1: Big Bang vs Incremental Refactoring

**Agent 10 (Documentation):** Suggested big-bang rewrite for clean slate
**Agent 7 (Testing):** Strongly opposed - "No tests exist, big-bang is suicide!"
**Agent 1 (Architecture):** Agreed with Agent 7 - "Incremental with tests at each step"
**Agent 3 (Dependency):** "Cannot refactor without breaking things - need tests first"

**CONSENSUS:** ✅ **Incremental refactoring with test coverage at each phase**

### Debate 2: Keep Procedural vs Full OOP

**Agent 6 (Inheritance):** "Current procedural design is LSP-compliant by avoiding inheritance"
**Agent 4 (Interfaces):** "But it's untestable and violates SRP everywhere"
**Agent 2 (Data Model):** "Dictionaries everywhere = primitive obsession anti-pattern"
**Agent 8 (Code Quality):** "25-30% code duplication - needs abstraction"

**CONSENSUS:** ✅ **Move to OOP with design patterns, but avoid deep inheritance hierarchies**

### Debate 3: Type Hints vs Runtime Validation

**Agent 4 (Interfaces):** "TypedDict and Protocols for gradual typing"
**Agent 2 (Data Model):** "Dataclasses with validation for type safety"
**Agent 9 (Error Handling):** "Need runtime validation - types alone won't catch bad data"

**CONSENSUS:** ✅ **Both: Type hints + mypy + runtime validation in constructors**

### Debate 4: Dependency Injection Strategy

**Agent 3 (Dependency):** "100% hard-coded dependencies - severe DIP violation"
**Agent 5 (Extensibility):** "Cannot extend without modifying code - severe OCP violation"
**Agent 7 (Testing):** "Cannot test without DI - currently impossible to mock"

**CONSENSUS:** ✅ **Full dependency injection with abstract interfaces**

### Debate 5: Error Handling Approach

**Agent 9 (Error Handling):** "Only 3.8% of code handles errors, 2 bare except blocks"
**Agent 7 (Testing):** "Silent failures everywhere - cannot test error paths"
**Agent 10 (Documentation):** "No error documentation exists"

**CONSENSUS:** ✅ **Custom exception hierarchy + structured logging + comprehensive error handling**

---

## CRITICAL FINDINGS (ALL AGENTS AGREE)

### 🔴 CRITICAL Issue #1: Global State
**File:** `/home/user/aamva-id-faker/generate_licenses.py:51`
```python
fake = Faker()  # GLOBAL MUTABLE STATE
```

**Impact:**
- Agent 3: "Violates DIP - tight coupling to Faker"
- Agent 7: "Cannot test - impossible to mock"
- Agent 2: "All data generation tied to this instance"
- **50+ function calls depend on this global**

### 🔴 CRITICAL Issue #2: God Function
**File:** `/home/user/aamva-id-faker/generate_licenses.py:275-357` (83 lines)
```python
def generate_license_data(state=None):
    # 12+ responsibilities in one function!
```

**Impact:**
- Agent 1: "Severe SRP violation"
- Agent 2: "Impossible to test individual concerns"
- Agent 7: "Cannot mock sub-behaviors"
- Agent 8: "High cyclomatic complexity"

### 🔴 CRITICAL Issue #3: No Error Handling
**Impact:**
- Agent 9: "Only 5 error blocks in 786 lines (0.6%)"
- Agent 7: "Cannot test error paths"
- Agent 1: "Silent failures hide bugs"

### 🔴 CRITICAL Issue #4: No Tests
**Impact:**
- Agent 7: "0% test coverage - cannot refactor safely"
- Agent 3: "Architecture prevents testing"
- Agent 10: "Excellent documentation but zero test implementation"

### 🔴 CRITICAL Issue #5: Primitive Obsession
**Impact:**
- Agent 2: "Dictionaries everywhere - no type safety"
- Agent 4: "No interfaces or protocols"
- Agent 8: "Magic strings throughout"

---

## REFACTORING STRATEGY (CONSENSUS-DRIVEN)

### Phase 0: Preparation (Week 0) - 16 hours

**Objective:** Set up infrastructure without touching production code

**Tasks:**
1. Set up pytest infrastructure
2. Create test directory structure
3. Add development dependencies (pytest, mypy, black, isort)
4. Configure pre-commit hooks
5. Set up CI/CD pipeline
6. Create feature flags for gradual rollout

**Deliverables:**
- Working test infrastructure
- Linting and formatting configured
- CI/CD pipeline running

### Phase 1: Value Objects & Type Safety (Weeks 1-3) - 60 hours

**Objective:** Replace dictionaries with type-safe dataclasses

**Agent Consensus:**
- Agent 2: "Priority 1 - foundation for everything"
- Agent 4: "Enables interface definitions"
- Agent 7: "Makes testing possible"

**Tasks:**
1. Create value objects (Week 1):
   - `PersonalInfo` dataclass
   - `PhysicalCharacteristics` dataclass
   - `Address` dataclass
   - `LicenseDates` dataclass
   - `License` dataclass (immutable)

2. Add validation (Week 1):
   - `__post_init__` validators
   - Custom validation exceptions
   - Type hints everywhere

3. Backward compatibility (Week 2):
   - `to_dict()` methods for legacy code
   - `from_dict()` class methods
   - Gradual migration path

4. Write tests (Week 2-3):
   - 80+ unit tests for value objects
   - Property-based testing with hypothesis
   - Validation edge case testing

**Success Criteria:**
- ✅ All value objects are immutable
- ✅ 100% test coverage on value objects
- ✅ mypy passes with --strict
- ✅ Legacy code still works via to_dict()

### Phase 2: Builder Pattern (Week 4) - 30 hours

**Objective:** Replace complex construction with fluent builders

**Agent Consensus:**
- Agent 8: "Eliminates duplication in construction"
- Agent 10: "Classic pattern for complex objects"
- Agent 7: "Makes testing much easier"

**Tasks:**
1. Implement `LicenseBuilder` with fluent interface
2. Implement sub-builders (PersonalInfoBuilder, etc.)
3. Add validation at build time
4. Write 40+ tests for builders
5. Refactor `generate_license_data()` to use builder

**Success Criteria:**
- ✅ Fluent API working
- ✅ Validation at build time
- ✅ 40+ builder tests passing
- ✅ Reduced complexity in license generation

### Phase 3: Dependency Injection (Weeks 5-6) - 40 hours

**Objective:** Eliminate global state, enable testing

**Agent Consensus:**
- Agent 3: "Critical for DIP compliance"
- Agent 7: "Absolutely required for testing"
- Agent 5: "Enables extensibility"

**Tasks:**
1. Create abstract interfaces:
   - `DataGenerator` protocol
   - `LicenseNumberGenerator` interface
   - `BarcodeEncoder` interface
   - `OutputGenerator` interface

2. Implement concrete classes:
   - `FakerDataGenerator` (wraps Faker)
   - `PDF417BarcodeEncoder` (wraps pdf417)

3. Remove global `fake` instance:
   - Pass dependencies to constructors
   - Use dependency injection throughout

4. Create `Application` class:
   - Main orchestrator
   - Manages all dependencies
   - Dependency injection container

**Success Criteria:**
- ✅ No global state
- ✅ All dependencies injected
- ✅ Can mock all external dependencies
- ✅ 60+ tests with mocked dependencies

### Phase 4: Strategy Pattern (Weeks 7-8) - 60 hours

**Objective:** Replace 30-state lambda dictionary with testable strategies

**Agent Consensus:**
- Agent 5: "Critical OCP violation - highest priority"
- Agent 8: "30+ lambda duplications"
- Agent 10: "Classic Strategy pattern use case"

**Tasks:**
1. Create `LicenseNumberStrategy` ABC (Week 7):
   - `generate()` method
   - `validate()` method
   - `format_pattern` property

2. Implement 51 state strategies (Week 7-8):
   - One class per state
   - Unit tests for each strategy
   - Regex validation patterns

3. Create `LicenseNumberFactory` (Week 8):
   - Registry pattern
   - State strategy lookup
   - Default fallback strategy

4. Write comprehensive tests (Week 8):
   - 100+ strategy tests
   - Property-based testing
   - Format validation tests

**Success Criteria:**
- ✅ All 51 states have strategies
- ✅ Each strategy independently tested
- ✅ Factory provides correct strategy
- ✅ Can validate generated numbers

### Phase 5: Error Handling (Week 9) - 30 hours

**Objective:** Add robust error handling throughout

**Agent Consensus:**
- Agent 9: "Currently only 3.8% error handling"
- Agent 7: "Cannot test error paths"
- Agent 1: "Silent failures hide bugs"

**Tasks:**
1. Create exception hierarchy:
   - `AAMVAError` (base)
   - `DataGenerationError`
   - `EncodingError`
   - `DocumentGenerationError`
   - `ValidationError`

2. Replace bare except blocks:
   - Lines 464, 527 need specific exceptions
   - Add proper exception chaining

3. Add structured logging:
   - Replace all `print()` statements
   - Use Python logging module
   - Add log levels (DEBUG, INFO, WARNING, ERROR)

4. Add error recovery:
   - Retry logic for file I/O
   - Fallback behaviors
   - Graceful degradation

**Success Criteria:**
- ✅ No bare except blocks
- ✅ Custom exception hierarchy
- ✅ All errors logged
- ✅ 40+ error path tests

### Phase 6: Barcode Encoding (Week 10) - 40 hours

**Objective:** Refactor barcode encoding with Chain of Responsibility

**Agent Consensus:**
- Agent 8: "Complex monolithic function needs decomposition"
- Agent 10: "Chain of Responsibility pattern perfect fit"
- Agent 2: "Subfile processing duplicated"

**Tasks:**
1. Create encoder chain:
   - `HeaderEncoder`
   - `SubfileDesignatorEncoder`
   - `SubfileDataEncoder`

2. Create `Subfile` hierarchy:
   - `Subfile` ABC
   - `DLSubfile`
   - `StateSubfile`
   - `SubfileBuilder`

3. Refactor `format_barcode_data()`:
   - Use encoder chain
   - Eliminate duplication
   - Add validation

4. Write tests:
   - 50+ encoding tests
   - AAMVA compliance tests
   - Round-trip encode/decode tests

**Success Criteria:**
- ✅ Chain of Responsibility working
- ✅ No code duplication
- ✅ AAMVA compliance verified
- ✅ 50+ encoding tests passing

### Phase 7: Output Generation (Weeks 11-12) - 60 hours

**Objective:** Refactor document generation with Factory + Template Method

**Agent Consensus:**
- Agent 5: "Cannot add formats without modifying main()"
- Agent 8: "Significant duplication in PDF/DOCX generation"
- Agent 10: "Factory + Template Method eliminate duplication"

**Tasks:**
1. Create `OutputGenerator` interface (Week 11):
   - `generate()` method
   - `supported_format` property
   - `is_available()` method

2. Implement Template Method (Week 11):
   - `CardDocumentGenerator` ABC
   - Common algorithm skeleton
   - Subclass-specific implementations

3. Implement concrete generators (Week 11-12):
   - `PDFOutputGenerator`
   - `DOCXOutputGenerator`
   - `ODTOutputGenerator` (fix or remove)

4. Create `OutputGeneratorFactory` (Week 12):
   - Registry pattern
   - Auto-discovery
   - Plugin support

5. Refactor card formatting (Week 12):
   - Extract `CardFormatter` strategies
   - Eliminate 3 instances of duplication
   - Single source of truth

**Success Criteria:**
- ✅ Factory pattern working
- ✅ Template Method eliminates duplication
- ✅ Can add formats without modifying main()
- ✅ 60+ output tests passing

### Phase 8: Repository Pattern (Week 13) - 30 hours

**Objective:** Abstract file I/O for testability

**Agent Consensus:**
- Agent 3: "Direct file I/O everywhere"
- Agent 7: "Cannot test without actual filesystem"
- Agent 10: "Repository pattern standard solution"

**Tasks:**
1. Create `LicenseRepository` interface:
   - `save_license()` method
   - `save_barcode()` method
   - `load_license()` method

2. Implement `FileSystemRepository`:
   - File-based persistence
   - Directory management
   - Path configuration

3. Create mock repository for tests:
   - In-memory storage
   - Fast tests
   - No file I/O

4. Refactor I/O operations:
   - Use repository throughout
   - Inject repository dependency

**Success Criteria:**
- ✅ Repository pattern working
- ✅ Tests use mock repository
- ✅ No direct file I/O in business logic
- ✅ 30+ repository tests

### Phase 9: Configuration (Week 14) - 20 hours

**Objective:** Externalize configuration, remove magic numbers

**Agent Consensus:**
- Agent 5: "Hard-coded config throughout"
- Agent 8: "Magic numbers everywhere"
- Agent 10: "Configuration object essential"

**Tasks:**
1. Create configuration dataclasses:
   - `AAMVAConfig`
   - `BarcodeConfig`
   - `OutputConfig`
   - `ApplicationConfig`

2. Support config files:
   - YAML file support
   - JSON file support
   - Environment variables

3. Configuration hierarchy:
   - Built-in defaults
   - Config file overrides
   - Environment variable overrides
   - CLI argument overrides

4. Remove magic numbers:
   - Extract all constants
   - Document all values

**Success Criteria:**
- ✅ All magic numbers eliminated
- ✅ YAML configuration working
- ✅ Environment variables supported
- ✅ Configuration validated

### Phase 10: Testing & Documentation (Weeks 15-16) - 60 hours

**Objective:** Achieve 80%+ test coverage, complete documentation

**Agent Consensus:**
- Agent 7: "Currently 0% coverage - need comprehensive tests"
- Agent 10: "Excellent docs, but need code-level docstrings"

**Tasks:**
1. Integration tests (Week 15):
   - End-to-end license generation
   - All output formats
   - All 51 states
   - Barcode decoding validation

2. Performance tests (Week 15):
   - Batch generation benchmarks
   - Memory profiling
   - Optimization opportunities

3. Documentation (Week 16):
   - Add docstrings to all classes/functions
   - Generate Sphinx documentation
   - Create tutorials
   - Write ADRs (Architecture Decision Records)

4. Coverage analysis (Week 16):
   - Generate coverage report
   - Identify gaps
   - Write additional tests
   - Achieve 80%+ coverage

**Success Criteria:**
- ✅ 80%+ test coverage
- ✅ All functions have docstrings
- ✅ Sphinx docs generated
- ✅ Performance benchmarks documented

---

## IMPLEMENTATION INSTRUCTIONS FOR CLAUDE

### Using Multi-Agent Approach (Up to 30 Agents)

**Strategy:** Parallelize work across agents for maximum efficiency

#### Agent Assignment Matrix

**Phase 1: Value Objects (3 agents in parallel)**
- Agent A: Create PersonalInfo + Address dataclasses
- Agent B: Create PhysicalCharacteristics + LicenseDates
- Agent C: Write all validation tests

**Phase 2: Builder Pattern (2 agents)**
- Agent A: Implement LicenseBuilder
- Agent B: Write builder tests

**Phase 3: Dependency Injection (4 agents)**
- Agent A: Create abstract interfaces
- Agent B: Implement FakerDataGenerator
- Agent C: Implement BarcodeEncoder
- Agent D: Write DI tests

**Phase 4: Strategy Pattern (30 agents in parallel!)**
- Agents 1-25: Each implements 2-3 state strategies
- Agents 26-28: Write strategy tests (3 agents, ~33 states each)
- Agent 29: Implement LicenseNumberFactory
- Agent 30: Integration testing

**Phase 5: Error Handling (3 agents)**
- Agent A: Create exception hierarchy + logging
- Agent B: Replace all error handling
- Agent C: Write error path tests

**Phase 6: Barcode Encoding (4 agents)**
- Agent A: Create encoder chain
- Agent B: Create Subfile hierarchy
- Agent C: Refactor format_barcode_data()
- Agent D: Write encoding tests

**Phase 7: Output Generation (6 agents)**
- Agent A: Create OutputGenerator interface
- Agent B: Implement PDFOutputGenerator
- Agent C: Implement DOCXOutputGenerator
- Agent D: Create OutputGeneratorFactory
- Agent E: Extract CardFormatter
- Agent F: Write output tests

**Phase 8: Repository Pattern (2 agents)**
- Agent A: Implement FileSystemRepository
- Agent B: Write repository tests

**Phase 9: Configuration (2 agents)**
- Agent A: Create config dataclasses + loaders
- Agent B: Remove magic numbers throughout

**Phase 10: Testing & Documentation (8 agents)**
- Agents 1-4: Integration tests (one agent per output format)
- Agents 5-6: Performance tests
- Agents 7-8: Documentation (docstrings + Sphinx)

#### Parallel Execution Commands

```bash
# Phase 4 example: Generate all 51 state strategies in parallel
claude agent create --type=general --parallel --count=30 \
  --task="Implement state license number strategies" \
  --distribute-states="AL,AK,AZ,..." \
  --output-dir="aamva_faker/strategies/states/"

# Each agent gets 2-3 states and implements:
# 1. StateStrategy class
# 2. Unit tests
# 3. Validation regex

# Agents work independently and merge results
```

### Quality Gates (Must Pass Before Next Phase)

**After Each Phase:**
1. ✅ All tests pass (pytest)
2. ✅ Type checking passes (mypy --strict)
3. ✅ Linting passes (black, isort, flake8)
4. ✅ Coverage maintained or improved
5. ✅ Performance not degraded (benchmarks)
6. ✅ Documentation updated
7. ✅ Code review passed (GitHub PR)

### Rollback Strategy

**If phase fails:**
1. Git revert to previous phase
2. Analyze failure causes
3. Adjust approach
4. Retry phase with modifications

### Success Metrics

**Final Assessment Criteria:**
- ✅ Test coverage: 80%+ (currently 0%)
- ✅ SOLID compliance: 8/10+ (currently 2/10)
- ✅ Type safety: mypy --strict passes (currently fails)
- ✅ Error handling: No bare excepts (currently 2)
- ✅ Code duplication: <5% (currently 25-30%)
- ✅ Testability: 9/10 (currently 2/10)
- ✅ Performance: No degradation
- ✅ Functionality: All existing features work

---

## FINAL PROJECT STRUCTURE

```
aamva-id-faker/
├── aamva_faker/                    # Main package
│   ├── __init__.py
│   ├── __main__.py
│   ├── models/                     # Value objects (Phase 1)
│   │   ├── license.py
│   │   ├── personal.py
│   │   ├── physical.py
│   │   ├── address.py
│   │   └── dates.py
│   ├── builders/                   # Builder pattern (Phase 2)
│   │   ├── license_builder.py
│   │   └── sub_builders.py
│   ├── generators/                 # Data generation (Phase 3)
│   │   ├── base.py
│   │   ├── faker_generator.py
│   │   └── license_generator.py
│   ├── strategies/                 # Strategy pattern (Phase 4)
│   │   ├── base.py
│   │   ├── states/                 # 51 state strategies
│   │   │   ├── california.py
│   │   │   ├── florida.py
│   │   │   └── ... (49 more)
│   │   └── factory.py
│   ├── encoding/                   # Barcode encoding (Phase 6)
│   │   ├── encoders.py
│   │   ├── subfiles.py
│   │   └── aamva.py
│   ├── rendering/                  # Output generation (Phase 7)
│   │   ├── base.py
│   │   ├── pdf_generator.py
│   │   ├── docx_generator.py
│   │   ├── formatters.py
│   │   └── factory.py
│   ├── repositories/               # Repository pattern (Phase 8)
│   │   ├── base.py
│   │   └── filesystem.py
│   ├── config/                     # Configuration (Phase 9)
│   │   ├── models.py
│   │   └── loader.py
│   ├── exceptions.py               # Error handling (Phase 5)
│   └── utils/
│       ├── logging.py
│       └── validation.py
├── tests/                          # Test suite (Phase 10)
│   ├── unit/                       # 200+ unit tests
│   ├── integration/                # 40+ integration tests
│   └── fixtures/
├── docs/                           # Documentation
│   ├── api/
│   ├── tutorials/
│   └── adr/                        # Architecture Decision Records
├── config/
│   ├── default.yaml
│   └── development.yaml
├── pyproject.toml
└── README.md
```

---

## RISK MITIGATION

### Risk 1: Breaking Existing Functionality
**Mitigation:**
- Maintain backward compatibility through Phase 7
- Feature flags for gradual rollout
- Extensive integration tests
- Parallel old/new implementations during transition

### Risk 2: Agent Coordination Failures
**Mitigation:**
- Clear interface contracts between agents
- Integration tests after each parallel phase
- Central coordinator agent reviews all work
- Git branch per agent with PR review

### Risk 3: Performance Degradation
**Mitigation:**
- Benchmark before refactoring
- Performance tests in CI/CD
- Profiling after each phase
- Optimize if >10% degradation

### Risk 4: Scope Creep
**Mitigation:**
- Strict phase boundaries
- No new features during refactoring
- Quality gates enforce completion
- Document deferred improvements

---

## EFFORT ESTIMATION

### Total Effort: 480 hours (12 weeks full-time)

| Phase | Hours | Agents | Parallel | Wall Time |
|-------|-------|--------|----------|-----------|
| Phase 0: Preparation | 16 | 1 | No | 2 days |
| Phase 1: Value Objects | 60 | 3 | Yes | 5 days |
| Phase 2: Builder | 30 | 2 | Yes | 4 days |
| Phase 3: DI | 40 | 4 | Yes | 3 days |
| Phase 4: Strategy | 60 | 30 | Yes | 1 day! |
| Phase 5: Errors | 30 | 3 | Yes | 3 days |
| Phase 6: Encoding | 40 | 4 | Yes | 3 days |
| Phase 7: Output | 60 | 6 | Yes | 3 days |
| Phase 8: Repository | 30 | 2 | Yes | 4 days |
| Phase 9: Config | 20 | 2 | Yes | 3 days |
| Phase 10: Testing/Docs | 60 | 8 | Yes | 2 weeks |
| **Total** | **480** | **Up to 30** | - | **6 weeks** |

**With multi-agent parallelization: 480 hours → 6 weeks wall time**

---

## CONCLUSION

This master plan represents the consensus of 10 specialized AI agents analyzing the AAMVA ID Faker from every angle. The refactoring strategy is aggressive but achievable, transforming a functional script into a professional library that:

1. ✅ Complies with SOLID principles (9/10)
2. ✅ Has comprehensive test coverage (80%+)
3. ✅ Is fully type-safe (mypy --strict)
4. ✅ Handles errors gracefully
5. ✅ Is easily extensible (plugins, strategies)
6. ✅ Has zero code duplication
7. ✅ Maintains all existing functionality
8. ✅ Performs as well or better

**The agents have spoken. The path is clear. Let's build something amazing.**

---

**Plan Author:** Multi-Agent Synthesis (10 agents)
**Plan Approved By:** All agents in consensus
**Ready for Execution:** Yes
**Confidence Level:** HIGH (9/10)

**Next Step:** Commit this plan and begin Phase 0 preparation.
