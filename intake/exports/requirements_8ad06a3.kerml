package rail::railweb {

  // --- Requirement Definitions
  requirement def FeatureReq "Functional capability";
  requirement def NFR "Nonfunctional requirement";
  requirement def ConstraintReq "Design/operational constraint";
  requirement def Milestone "Milestone window & DoD";
  requirement def Risk "Risk record";

  // --- Functional Features (System)
  requirement FeatureReq spec_library id = "req:rail/railweb/feature/spec-library" {
    text = "Provide a cited reference library of model railroading specifications and standards across target scales (N, HO, S, O, G, Z, TT).";
    rationale = "Enable accurate planning and validation for hobbyists and clubs.";
    verify = Inspection;
    source = "intake/scope.yml@8ad06a3";
    type = System;
    acceptance = "Users can look up a spec by scale with a cited value.";
  }

  requirement FeatureReq scale_conversion id = "req:rail/railweb/feature/scale-conversion" {
    text = "Provide calculators to convert real-world measurements by selected model scale with documented rounding rules.";
    verify = Test;
    source = "intake/scope.yml@8ad06a3";
    type = System;
  }

  requirement FeatureReq guidance_themes id = "req:rail/railweb/feature/guidance-themes" {
    text = "Publish guidance for automation and scenery as structured, cited checklists.";
    verify = Inspection;
    source = "intake/scope.yml@8ad06a3";
    type = System;
  }

  requirement FeatureReq navigation_search id = "req:rail/railweb/feature/navigation-search" {
    text = "Provide basic navigation and search to locate specs and guides.";
    verify = Demonstration;
    source = "intake/scope.yml@8ad06a3";
    type = System;
  }

  requirement FeatureReq realtime_control id = "req:rail/railweb/feature/realtime-control" {
    text = "Provide local/network-limited real-time layout control (e.g., throttle, turnout/route actions) on documented interfaces.";
    verify = Demonstration;
    source = "intake/scope.yml@8ad06a3";
    type = System;
  }

  requirement FeatureReq dcc_programming id = "req:rail/railweb/feature/dcc-programming" {
    text = "Provide DCC CV read/write in service and ops modes with audit logging.";
    verify = Test;
    source = "intake/scope.yml@8ad06a3";
    type = System;
  }

  requirement FeatureReq sim_cad_integration id = "req:rail/railweb/feature/sim-cad-integration" {
    text = "Provide import/export for at least one track-plan format and enable a basic virtual operating session.";
    verify = Demonstration;
    source = "intake/scope.yml@8ad06a3";
    type = System;
  }

  // --- Nonfunctional Requirements
  requirement NFR content_completeness id = "nfr:rail/railweb/content/completeness-20-specs" {
    text = "At launch, publish ≥20 cited specification entries across target scales.";
    measure = "count(spec_entries)";
    target = ">= 20";
    units = "entries";
    condition = "by milestone M6: Launch Baseline";
    verify = Inspection;
    source = "intake/success_criteria.yaml@8ad06a3";
    type = Nonfunctional(compliance);
  }

  requirement NFR findability id = "nfr:rail/railweb/usability/findability-3-clicks" {
    text = "A named specification is discoverable in ≤3 clicks from the landing page.";
    measure = "clicks_to_spec";
    target = "<= 3";
    units = "clicks";
    condition = "median over 10 representative tasks";
    verify = Test;
    type = Nonfunctional(usability);
    source = "intake/success_criteria.yaml@8ad06a3";
  }

  requirement NFR converter_accuracy id = "nfr:rail/railweb/quality/converter-accuracy" {
    text = "Scale conversion outputs match hand-checked results within documented rounding rules.";
    measure = "abs(delta_output)";
    target = "<= rounding_rule_tolerance";
    units = "scale_units";
    condition = "on curated test set of 50 cases";
    verify = Analysis;
    type = Nonfunctional(quality);
    source = "intake/success_criteria.yaml@8ad06a3";
  }

  // --- Constraints
  requirement ConstraintReq safety_ack id = "cons:rail/railweb/safety/ack-gate-live-control" {
    text = "Display prominent safety cautions and require explicit user acknowledgement before enabling live control.";
    verify = Inspection;
    type = Nonfunctional(safety);
    source = "intake/scope.yml@8ad06a3";
  }

  requirement ConstraintReq local_only_v1 id = "cons:rail/railweb/security/local-only-v1" {
    text = "V1 excludes cloud-hosted remote operations; restrict to local/network-limited scope.";
    verify = Analysis;
    type = Nonfunctional(security);
    source = "intake/scope.yml@8ad06a3";
  }

  requirement ConstraintReq licensing_attrib id = "cons:rail/railweb/compliance/licensing-attrib" {
    text = "Honor content licensing and attributions; each value cites source name, version, and date.";
    verify = Inspection;
    type = Nonfunctional(compliance);
    source = "intake/scope.yml, assumptions.yaml@8ad06a3";
  }

  // --- Milestones (management constraints)
  requirement Milestone M0 id = "ms:rail/railweb/M0" { text = "Initiation & Intake approval"; window = "2025-09-18/2025-09-24"; verify = Inspection; }
  requirement Milestone M1 id = "ms:rail/railweb/M1" { text = "IA & Content Map"; window = "2025-09-25/2025-10-01"; verify = Inspection; }
  requirement Milestone M2 id = "ms:rail/railweb/M2" { text = "Spec Corpus Curation"; window = "2025-10-02/2025-10-16"; verify = Inspection; }
  requirement Milestone M2A id = "ms:rail/railweb/M2A" { text = "Hardware & Protocol Inventory"; window = "2025-10-02/2025-10-09"; verify = Inspection; }
  requirement Milestone M3 id = "ms:rail/railweb/M3" { text = "Scale Converters MVP"; window = "2025-10-09/2025-10-23"; verify = Test; }
  requirement Milestone M4 id = "ms:rail/railweb/M4" { text = "Guidance Themes MVP"; window = "2025-10-16/2025-10-30"; verify = Inspection; }
  requirement Milestone M4A id = "ms:rail/railweb/M4A" { text = "Real-time Control MVP"; window = "2025-10-16/2025-10-30"; verify = Demonstration; }
  requirement Milestone M4B id = "ms:rail/railweb/M4B" { text = "DCC Programming MVP"; window = "2025-10-23/2025-11-06"; verify = Test; }
  requirement Milestone M4C id = "ms:rail/railweb/M4C" { text = "Simulation/CAD Integration MVP"; window = "2025-10-23/2025-11-06"; verify = Demonstration; }
  requirement Milestone M5 id = "ms:rail/railweb/M5" { text = "Beta Readiness"; window = "2025-11-07/2025-11-21"; verify = Inspection; }
  requirement Milestone M6 id = "ms:rail/railweb/M6" { text = "Launch Baseline"; window = "2025-11-22/2025-11-29"; verify = Inspection; }

  // --- Risk records (trace only, to risk register)
  requirement Risk R1 id = "risk:rail/railweb/R1" { text = "Standards usage rights/licensing may restrict reproduction"; }
  requirement Risk R2 id = "risk:rail/railweb/R2" { text = "Spec inaccuracies could misguide layouts"; }
  requirement Risk R3 id = "risk:rail/railweb/R3" { text = "Scale/standard variants create ambiguity"; }
  requirement Risk R4 id = "risk:rail/railweb/R4" { text = "Scope creep into tools/forums dilutes schedule"; }
  requirement Risk R5 id = "risk:rail/railweb/R5" { text = "Content curation slower than planned"; }
  requirement Risk R6 id = "risk:rail/railweb/R6" { text = "Unit confusion (metric/imperial) hurts usability"; }
  requirement Risk R7 id = "risk:rail/railweb/R7" { text = "Safety/liability concerns with live control"; }
  requirement Risk R8 id = "risk:rail/railweb/R8" { text = "Device/protocol fragmentation"; }
  requirement Risk R9 id = "risk:rail/railweb/R9" { text = "Latency/reliability issues degrade control"; }
  requirement Risk R10 id = "risk:rail/railweb/R10" { text = "Decoder CV differences complicate programming"; }
  requirement Risk R11 id = "risk:rail/railweb/R11" { text = "Licensing/format barriers for CAD/sim"; }
  requirement Risk R12 id = "risk:rail/railweb/R12" { text = "Security exposure if remote control expands"; }

  // --- Relationships
  spec_library refines content_completeness;
  scale_conversion refines converter_accuracy;
  navigation_search refines findability;
  realtime_control satisfies local_only_v1 and safety_ack;
  dcc_programming refines converter_accuracy;

} (See <attachments> above for file contents. You may not need to search or read the file again.)
