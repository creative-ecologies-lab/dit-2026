// TODO: add SVG image export

/**
 * Fractal_Tree fractalTreeApp constructor
 *
 */
function Fractal_Tree() {
  /**
		Constants
	**/

  /* Controls Variables */

  this.presetsOptions = null;
  this.currentPreset = null;

  this.lengthScale = 0;

  this.initialPoint = null;
  this.initialVector = null;

  this.treeSize = 0;
  this.treeSizeMin = 0;
  this.treeSizeMax = 0;
  this.treeSizeIncrement = 0;

  this.branchAngle = 0;
  this.branchAngleMin = 0;
  this.branchAngleMax = 0;
  this.branchAngleIncrement = 0;

  this.numberBranches = 0;
  this.numberBranchesMin = 0;
  this.numberBranchesMax = 0;
  this.numberBranchesIncrement = 0;

  this.spiralFactor = 0;
  this.spiralFactorMin = 0;
  this.spiralFactorMax = 0;
  this.spiralFactorIncrement = 0;

  this.recursionLevels = 0;
  this.recursionLevelsMin = 0;
  this.recursionLevelsMax = 0;
  this.recursionLevelsIncrement = 0;

  this.maxNumberNodesSVGExport = 0;

  this.drawTrunk = false;
  this.drawFruit = false;
  this.animateBranchAngle = false;

  // UI Variables
  this.presetSelect = null;

  this.inputFieldTreeSize = null;
  this.sliderTreeSize = null;

  this.inputFieldBranchAngle = null;
  this.sliderBranchAngle = null;

  this.checkDrawTrunk = null;
  this.checkDrawFruit = null;
  this.checkAnimateBranchAngle = null;

  this.buttonSaveSVG = null;

  this.progressbar = null;

  // Container components
  this.controlsContainer = null;
  this.animationContainer = null;

  this.window = null;

  /* View Variables */
  this.locationX = 0;
  this.locationY = 0;
  this.textDisplayLocationX = 0;
  this.textDisplayLocationY = 0;
  this.creditsLocationX = 0;
  this.creditsLocationY = 0;

  this.labelFontSize = 0;

  this.initialTimeStart = 0;

  this.colorRgbMap = {};

  // Calculated values
  this.circumference = 0;
  this.pointCircleCenter = 0;
  this.pointCircleStart = 0;

  this.contentGroup = null;
  this.detailsGroup = null;

  this.initialized = false;

  this.iterations = 0;
}

/**
 * Fractal_Tree fractalTreeApp class
 *
 */
Fractal_Tree.prototype = {
  constructor: Fractal_Tree,

  initControls: function () {
    this.initControlsValues();
    this.initControlsContainer();
    this.initControlsUI();
  },
  initView: function () {
    this.initViewValues();
    this.initViewAnimation();

    this.updateUIValues();
    // Initialize Drawing
    this.contentGroup = fractalTreeApp.redraw(
      fractalTreeApp.contentGroup,
      fractalTreeApp.drawContent()
    );
  },
  initControlsValues: function () {
    this.window = $(window);

    this.lengthScale = 1.61803; // PHI

    this.initialPoint = new Point(
      this.window.width() / 3,
      this.window.height() / (3 / 2)
    );
    this.initialVector = new Point(0, -this.treeSize);

    this.treeSize = this.formatDecimal(
      0.3 * this.window.height(),
      this.treeSizeIncrement
    );
    this.treeSizeMin = 0;
    this.treeSizeMax = this.treeSize * 3;
    this.treeSizeIncrement = 1;

    this.branchAngle = 90;
    this.branchAngleMin = 0;
    this.branchAngleMax = 1080;
    this.branchAngleIncrement = 1;

    this.numberBranches = 2;
    this.numberBranchesMin = 1;
    this.numberBranchesMax = 8;
    this.numberBranchesIncrement = 1;

    this.spiralFactor = 0;
    this.spiralFactorMin = 0;
    this.spiralFactorMax = 10;
    this.spiralFactorIncrement = 1;

    this.recursionLevels = 7;
    this.recursionLevelsMin = 1;
    this.recursionLevelsMax = 10;
    this.recursionLevelsIncrement = 1;

    this.maxNumberNodesSVGExport = 7776;

    // Load Preset
    this.presetsOptions = this.generatePresets();

    // Initialize time
    this.initialTimeStart = Date.now();
  },
  generatePresets: function () {
    var presetsObject = {
      Default: {
        branchAngle: 40,
        spiralFactor: 0,
        numberBranches: 2,
        recursionLevels: 8,
        drawTrunk: true,
        drawFruit: false,
        animateBranchAngle: false
      },
      "Binary Fractal": {
        branchAngle: 70,
        spiralFactor: 0,
        numberBranches: 2,
        recursionLevels: 9,
        drawTrunk: true,
        drawFruit: false,
        animateBranchAngle: true
      },
      Dance: {
        branchAngle: 0,
        spiralFactor: 1,
        numberBranches: 2,
        recursionLevels: 3,
        drawTrunk: true,
        drawFruit: true,
        animateBranchAngle: true
      },
      Kaleidoscope: {
        branchAngle: 0,
        spiralFactor: 5,
        numberBranches: 6,
        recursionLevels: 3,
        drawTrunk: false,
        drawFruit: true,
        animateBranchAngle: true
      },
      "Honeycomb 1": {
        branchAngle: 300,
        spiralFactor: 1,
        numberBranches: 3,
        recursionLevels: 6,
        drawTrunk: false,
        drawFruit: false,
        animateBranchAngle: false
      },
      "Honeycomb 2": {
        branchAngle: 72,
        spiralFactor: 0,
        numberBranches: 4,
        recursionLevels: 7,
        drawTrunk: false,
        drawFruit: false,
        animateBranchAngle: false
      },
      "Polygons 1": {
        branchAngle: 216,
        spiralFactor: 1,
        numberBranches: 6,
        recursionLevels: 4,
        drawTrunk: false,
        drawFruit: false,
        animateBranchAngle: false
      },
      "Polygons 2": {
        branchAngle: 216,
        spiralFactor: 1,
        numberBranches: 6,
        recursionLevels: 7,
        drawTrunk: false,
        drawFruit: false,
        animateBranchAngle: false
      },
      "Flower of Life": {
        branchAngle: 54,
        spiralFactor: 1,
        numberBranches: 5,
        recursionLevels: 7,
        drawTrunk: false,
        drawFruit: false,
        animateBranchAngle: false
      },
      "Spiral 1": {
        branchAngle: 40,
        spiralFactor: 1,
        numberBranches: 2,
        recursionLevels: 9,
        drawTrunk: true,
        drawFruit: false,
        animateBranchAngle: true
      },
      "Spiral 2": {
        branchAngle: 40,
        spiralFactor: 1,
        numberBranches: 3,
        recursionLevels: 6,
        drawTrunk: true,
        drawFruit: false,
        animateBranchAngle: true
      },
      "Spiral 3": {
        branchAngle: 200,
        spiralFactor: 3,
        numberBranches: 2,
        recursionLevels: 10,
        drawTrunk: true,
        drawFruit: false,
        animateBranchAngle: false
      },
      Bloom: {
        branchAngle: 25,
        spiralFactor: 1,
        numberBranches: 3,
        recursionLevels: 9,
        drawTrunk: true,
        drawFruit: false,
        animateBranchAngle: false
      },
      Pinwheel: {
        branchAngle: 216,
        spiralFactor: 4,
        numberBranches: 5,
        recursionLevels: 5,
        drawTrunk: true,
        drawFruit: false,
        animateBranchAngle: false
      },
      Canopy: {
        branchAngle: 30,
        spiralFactor: 0,
        numberBranches: 4,
        recursionLevels: 7,
        drawTrunk: true,
        drawFruit: false,
        animateBranchAngle: false
      },
      Grid: {
        branchAngle: 180,
        spiralFactor: 0,
        numberBranches: 2,
        recursionLevels: 10,
        drawTrunk: true,
        drawFruit: false,
        animateBranchAngle: false
      },
      "Holiday 1": {
        branchAngle: 240,
        spiralFactor: 1,
        numberBranches: 3,
        recursionLevels: 8,
        drawTrunk: true,
        drawFruit: false,
        animateBranchAngle: false
      },
      "Holiday 2": {
        branchAngle: 108,
        spiralFactor: 0,
        numberBranches: 3,
        recursionLevels: 10,
        drawTrunk: true,
        drawFruit: false,
        animateBranchAngle: false
      },
      Star: {
        branchAngle: 108,
        spiralFactor: 3,
        numberBranches: 5,
        recursionLevels: 6,
        drawTrunk: false,
        drawFruit: false,
        animateBranchAngle: false
      },
      Pentagon: {
        branchAngle: 72,
        spiralFactor: 0,
        numberBranches: 5,
        recursionLevels: 7,
        drawTrunk: false,
        drawFruit: false,
        animateBranchAngle: false
      },
      Network: {
        branchAngle: 270,
        spiralFactor: 7,
        numberBranches: 3,
        recursionLevels: 9,
        drawTrunk: false,
        drawFruit: false,
        animateBranchAngle: false
      }
    };
    return presetsObject;
  },
  loadPreset: function (presetsOptions, presetName) {
    var preset = presetsOptions[presetName];

    this.branchAngle = preset.branchAngle;
    this.spiralFactor = preset.spiralFactor;
    this.numberBranches = preset.numberBranches;
    this.recursionLevels = preset.recursionLevels;
    this.drawTrunk = preset.drawTrunk;
    this.drawFruit = preset.drawFruit;
    this.animateBranchAngle = preset.animateBranchAngle;

    if (this.contentGroup) {
      this.contentGroup = fractalTreeApp.redraw(
        fractalTreeApp.contentGroup,
        fractalTreeApp.drawContent()
      );
    }
  },
  initControlsContainer: function () {
    // UI Components
    this.presetSelect = $("#presetSelect");

    this.inputFieldTreeSize = $("#inputFieldTreeSize");
    this.sliderTreeSize = $("#sliderTreeSize");

    this.inputFieldBranchAngle = $("#inputFieldBranchAngle");
    this.sliderBranchAngle = $("#sliderBranchAngle");

    this.inputFieldNumberBranches = $("#inputFieldNumberBranches");
    this.sliderNumberBranches = $("#sliderNumberBranches");

    this.inputFieldSpiralFactor = $("#inputFieldSpiralFactor");
    this.sliderSpiralFactor = $("#sliderSpiralFactor");

    this.inputFieldRecursionLevels = $("#inputFieldRecursionLevels");
    this.sliderRecursionLevels = $("#sliderRecursionLevels");

    this.progressbar = $("#progressbar");

    this.checkDrawTrunk = $("#checkDrawTrunk");
    this.checkDrawFruit = $("#checkDrawFruit");
    this.checkAnimateBranchAngle = $("#checkAnimateBranchAngle");

    this.buttonSaveSVG = $("#buttonSaveSVG");

    // Container components
    this.controlsContainer = $("#controls");
    this.animationContainer = $("#animation");
  },
  initControlsUI: function () {
    var fractalTreeApp = this;

    /* Select Preset */
    this.presetSelect.selectmenu({
      change: function (event, data) {
        fractalTreeApp.currentPreset = data.item.value;
        fractalTreeApp.loadPreset(
          fractalTreeApp.presetsOptions,
          fractalTreeApp.currentPreset
        );
        fractalTreeApp.updateUIValues();
      }
    });
    // Select first preset
    this.currentPreset = Object.keys(this.presetsOptions)[0];
    this.loadPreset(this.presetsOptions, this.currentPreset);

    /* Control Tree Size */
    this.inputFieldTreeSize.attr("min", this.treeSizeMin);
    this.inputFieldTreeSize.attr("max", this.treeSizeMax);
    this.inputFieldTreeSize.attr("step", this.treeSizeIncrement);
    this.inputFieldTreeSize.change(function () {
      var value = fractalTreeApp.formatDecimal(
        this.value,
        fractalTreeApp.treeSizeIncrement
      );
      fractalTreeApp.treeSize = value;
      fractalTreeApp.contentGroup = fractalTreeApp.redraw(
        fractalTreeApp.contentGroup,
        fractalTreeApp.drawContent()
      );
      fractalTreeApp.updateUIValues();
    });
    // Slider to control radius
    this.sliderTreeSize.slider({
      range: "min",
      min: this.treeSizeMin,
      max: this.treeSizeMax,
      value: this.radius,
      step: this.treeSizeIncrement,
      slide: function (event, ui) {
        fractalTreeApp.treeSize = fractalTreeApp.formatDecimal(
          ui.value,
          fractalTreeApp.treeSizeIncrement
        );
        fractalTreeApp.contentGroup = fractalTreeApp.redraw(
          fractalTreeApp.contentGroup,
          fractalTreeApp.drawContent()
        );
        fractalTreeApp.updateUIValues();
      }
    });

    /* Control Branch Angle */
    this.inputFieldBranchAngle.attr("min", this.branchAngleMin);
    this.inputFieldBranchAngle.attr("max", this.branchAngleMax);
    this.inputFieldBranchAngle.attr("step", this.branchAngleIncrement);
    this.inputFieldBranchAngle.change(function () {
      var value = fractalTreeApp.formatDecimal(
        this.value,
        fractalTreeApp.baseSpeedIncrement
      );
      fractalTreeApp.branchAngle = value;
      fractalTreeApp.contentGroup = fractalTreeApp.redraw(
        fractalTreeApp.contentGroup,
        fractalTreeApp.drawContent()
      );
      fractalTreeApp.updateUIValues();
    });
    // Slider to control base/number of points
    this.sliderBranchAngle.slider({
      range: "min",
      min: this.branchAngleMin,
      max: this.branchAngleMax,
      value: this.branchAngle,
      step: this.branchAngleIncrement,
      slide: function (event, ui) {
        //	  fractalTreeApp.base = fractalTreeApp.formatDecimal(ui.value, fractalTreeApp.baseSpeedIncrement);
        fractalTreeApp.branchAngle = fractalTreeApp.formatDecimal(
          ui.value,
          fractalTreeApp.branchAngleIncrement
        );
        fractalTreeApp.contentGroup = fractalTreeApp.redraw(
          fractalTreeApp.contentGroup,
          fractalTreeApp.drawContent()
        );
        fractalTreeApp.updateUIValues();
      }
    });

    /* Control Number of Branches */
    this.inputFieldNumberBranches.attr("min", this.numberBranchesMin);
    this.inputFieldNumberBranches.attr("max", this.numberBranchesMax);
    this.inputFieldNumberBranches.attr("step", this.numberBranchesIncrement);
    this.inputFieldNumberBranches.change(function () {
      var value = fractalTreeApp.formatDecimal(
        this.value,
        fractalTreeApp.numberBranchesIncrement
      );
      fractalTreeApp.numberBranches = value;
      fractalTreeApp.contentGroup = fractalTreeApp.redraw(
        fractalTreeApp.contentGroup,
        fractalTreeApp.drawContent()
      );
      fractalTreeApp.updateUIValues();
    });
    // Slider to control base/number of points
    this.sliderNumberBranches.slider({
      range: "min",
      min: this.numberBranchesMin,
      max: this.numberBranchesMax,
      value: this.numberBranches,
      step: this.numberBranchesIncrement,
      slide: function (event, ui) {
        fractalTreeApp.numberBranches = fractalTreeApp.formatDecimal(
          ui.value,
          fractalTreeApp.numberBranchesIncrement
        );
        fractalTreeApp.contentGroup = fractalTreeApp.redraw(
          fractalTreeApp.contentGroup,
          fractalTreeApp.drawContent()
        );
        fractalTreeApp.updateUIValues();
      }
    });

    /* Control Spiral Factor */
    this.inputFieldSpiralFactor.attr("min", this.spiralFactorMin);
    this.inputFieldSpiralFactor.attr("max", this.spiralFactorMax);
    this.inputFieldSpiralFactor.attr("step", this.spiralFactorIncrement);
    this.inputFieldSpiralFactor.change(function () {
      var value = fractalTreeApp.formatDecimal(
        this.value,
        fractalTreeApp.spiralFactorIncrement
      );
      fractalTreeApp.spiralFactor = value;
      fractalTreeApp.contentGroup = fractalTreeApp.redraw(
        fractalTreeApp.contentGroup,
        fractalTreeApp.drawContent()
      );
      fractalTreeApp.updateUIValues();
    });
    // Slider to control Spiral Factor
    this.sliderSpiralFactor.slider({
      range: "min",
      min: this.spiralFactorMin,
      max: this.spiralFactorMax,
      value: this.spiralFactor,
      step: this.spiralFactorIncrement,
      slide: function (event, ui) {
        fractalTreeApp.spiralFactor = fractalTreeApp.formatDecimal(
          ui.value,
          fractalTreeApp.spiralFactorIncrement
        );
        fractalTreeApp.contentGroup = fractalTreeApp.redraw(
          fractalTreeApp.contentGroup,
          fractalTreeApp.drawContent()
        );
        fractalTreeApp.updateUIValues();
      }
    });

    /* Control Recursion Level */
    this.inputFieldRecursionLevels.attr("min", this.recursionLevelsMin);
    this.inputFieldRecursionLevels.attr("max", this.recursionLevelsMax);
    this.inputFieldRecursionLevels.attr("step", this.recursionLevelsIncrement);
    this.inputFieldRecursionLevels.change(function () {
      var value = fractalTreeApp.formatDecimal(
        this.value,
        fractalTreeApp.recursionLevelsIncrement
      );
      fractalTreeApp.recursionLevels = value;
      fractalTreeApp.contentGroup = fractalTreeApp.redraw(
        fractalTreeApp.contentGroup,
        fractalTreeApp.drawContent()
      );
      fractalTreeApp.updateUIValues();
    });
    // Slider to control base/number of points
    this.sliderRecursionLevels.slider({
      range: "min",
      min: this.recursionLevelsMin,
      max: this.recursionLevelsMax,
      value: this.recursionLevels,
      step: this.recursionLevelsIncrement,
      slide: function (event, ui) {
        fractalTreeApp.recursionLevels = fractalTreeApp.formatDecimal(
          ui.value,
          fractalTreeApp.recursionLevelsIncrement
        );
        fractalTreeApp.contentGroup = fractalTreeApp.redraw(
          fractalTreeApp.contentGroup,
          fractalTreeApp.drawContent()
        );
        fractalTreeApp.updateUIValues();
      }
    });

    // Toggle button to control drawing the trunk
    this.checkDrawTrunk.button();
    this.checkDrawTrunk.click(function () {
      fractalTreeApp.drawTrunk = !fractalTreeApp.drawTrunk;
      fractalTreeApp.contentGroup = fractalTreeApp.redraw(
        fractalTreeApp.contentGroup,
        fractalTreeApp.drawContent()
      );
      fractalTreeApp.updateUIValues();
    });

    // Toggle button to control drawing the fruit
    this.checkDrawFruit.button();
    this.checkDrawFruit.click(function () {
      fractalTreeApp.drawFruit = !fractalTreeApp.drawFruit;
      fractalTreeApp.contentGroup = fractalTreeApp.redraw(
        fractalTreeApp.contentGroup,
        fractalTreeApp.drawContent()
      );
      fractalTreeApp.updateUIValues();
    });

    // Toggle button to control animation
    this.checkAnimateBranchAngle.button();
    this.checkAnimateBranchAngle.click(function () {
      fractalTreeApp.animateBranchAngle = !fractalTreeApp.animateBranchAngle;
      fractalTreeApp.contentGroup = fractalTreeApp.redraw(
        fractalTreeApp.contentGroup,
        fractalTreeApp.drawContent()
      );
      fractalTreeApp.updateUIValues();
    });

    // Button to export as SVG
    this.buttonSaveSVG.button();
    this.buttonSaveSVG.click(function () {
      // Disable the Save SVG button while running
      fractalTreeApp.buttonSaveSVG.attr("disabled", true);
      fractalTreeApp.buttonSaveSVG.attr("value", "Exporting SVG...");
      setTimeout(function () {
        fractalTreeApp.downloadAsSVG();
      }, 10);
    });

    $("#accordion").accordion({
      collapsible: true,
      active: false
    });
  },
  initViewValues: function () {
    this.resize();

    this.locationX = view.size.width / 2;
    this.locationY = view.size.height / (9 / 7);

    this.initialPoint = new Point(this.locationX, this.locationY);

    // Calculated values
    this.pointCircleCenter = new Point(this.locationX, this.locationY);
    this.pointCircleStart = new Point(
      this.locationX - this.radius,
      this.locationY
    );
  },
  initViewAnimation: function () {
    view.draw();
  },
  updateUITreeSize: function () {
    /* Radius */
    this.inputFieldTreeSize.val(this.treeSize);
    this.sliderTreeSize.slider("value", this.treeSize);
  },
  updateUIBranchAngle: function () {
    /* Base */
    this.inputFieldBranchAngle.val(this.branchAngle);
    this.sliderBranchAngle.slider("value", this.branchAngle);
  },
  updateUINumberBranches: function () {
    /* Number Branches */
    this.inputFieldNumberBranches.val(this.numberBranches);
    this.sliderNumberBranches.slider("value", this.numberBranches);
  },
  updateUISpiralFactor: function () {
    /* Spiral Factor */
    this.inputFieldSpiralFactor.val(this.spiralFactor);
    this.sliderSpiralFactor.slider("value", this.spiralFactor);
  },
  updateUIRecursionLevels: function () {
    /* Recursion Levels */
    this.inputFieldRecursionLevels.val(this.recursionLevels);
    this.sliderRecursionLevels.slider("value", this.recursionLevels);
  },
  updateUITrunk: function () {
    this.checkDrawTrunk.attr("checked", this.drawTrunk ? true : false);
    this.checkDrawTrunk.button("refresh");
  },
  updateUIFruit: function () {
    this.checkDrawFruit.attr("checked", this.drawFruit ? true : false);
    this.checkDrawFruit.button("refresh");
  },
  updateUIAnimateBranchAngle: function () {
    this.checkAnimateBranchAngle.attr(
      "checked",
      this.animateBranchAngle ? true : false
    );
    this.checkAnimateBranchAngle.button("refresh");
  },
  updateUIComplexityLevel: function () {
    var numberNodes = this.getNumberNodes();
    var complexityLevel = numberNodes * this.recursionLevels;
    $("#number-of-nodes").text(
      this.numberBranches + "^" + this.recursionLevels + " = " + numberNodes
    );
    if (complexityLevel <= 40000) {
      $("#complexity-level").text("Low ");
      $("#complexity-level").css("color", "green");
      $("#complexity-level-tooltip").attr(
        "title",
        "This animation should run smoothly."
      );
    } else if (complexityLevel <= 100000) {
      $("#complexity-level").text("Medium ");
      $("#complexity-level").css("color", "orange");
      $("#complexity-level-tooltip").attr(
        "title",
        "Performance may be slow. Reduce one of complexity sliders to improve."
      );
    } else {
      $("#complexity-level").text("High ");
      $("#complexity-level").css("color", "red");
      $("#complexity-level-tooltip").attr(
        "title",
        "Performance may be very slow. Reduce one of complexity sliders to improve."
      );
    }

    // Time estimate for SVG export (times based on tests done)
    this.buttonSaveSVG.attr("disabled", false);
    if (this.drawFruit) {
      numberNodes *= 2;
    }
    if (numberNodes <= 2187) {
      // R=7, B=3
      estimatedTimeText = "< 30 seconds";
    } else if (numberNodes <= 3125) {
      // R=5, B=5
      estimatedTimeText = "< 1 minute";
    } else if (numberNodes <= 4096) {
      // R=6, B=4
      estimatedTimeText = "< 1.5 minutes";
    } else if (numberNodes <= 8192) {
      // R=5, B=6: numberNodes = 7776
      // R=6. B=4, drawFruit=true: numberNodes=4096*2=8192
      estimatedTimeText = "< 3 minutes";
    } else if (numberNodes > this.maxNumberNodesSVGExport) {
      estimatedTimeText = "N/A (too many nodes)";
      this.buttonSaveSVG.attr("disabled", true);
    } else {
      estimatedTimeText = "unknown";
    }
    $("#export-svg-time-estimate").text(estimatedTimeText);
  },
  updateUIValues: function () {
    // Update UI values of the slider controls
    this.updateUITreeSize();
    this.updateUIBranchAngle();
    this.updateUINumberBranches();
    this.updateUIRecursionLevels();
    this.updateUISpiralFactor();
    this.updateUIComplexityLevel();
    this.updateUIAnimateBranchAngle();

    this.updateUITrunk();
    this.updateUIFruit();
  },
  updateAnimateBase: function () {
    if (
      (!this.animateBase && this.baseSpeed > 0) ||
      (this.animateBase && this.baseSpeed == 0)
    ) {
      this.animateBase = !this.animateBase;
    }
  },
  updateAnimateMultiplyFactor: function () {
    if (
      (!this.animateMultiplyFactor && this.multiplyFactorSpeed > 0) ||
      (this.animateMultiplyFactor && this.multiplyFactorSpeed == 0)
    ) {
      this.animateMultiplyFactor = !this.animateMultiplyFactor;
    }
  },
  getNumberNodes: function () {
    return Math.pow(this.numberBranches, this.recursionLevels);
  },
  downloadAsSVG: function (fileName) {
    // R/B=10/2 nodes=1024: 7 seconds
    // R/B=7/3 nodes=2187: 11 seconds
    // R/B=5/5 nodes=3125: 25 seconds
    // R/B=6/4 nodes=4096: 47 seconds
    // R/B=5/6 nodes=7776: 1 minute, 41 seconds
    if (this.getNumberNodes() <= this.maxNumberNodesSVGExport) {
      if (!fileName) {
        fileName =
          "fractaltree_a" +
          this.branchAngle +
          "_f" +
          this.spiralFactor +
          "_b" +
          this.numberBranches +
          "_r" +
          this.recursionLevels;
      }

      var url =
        "data:image/svg+xml;utf8," +
        encodeURIComponent(paper.project.exportSVG({ asString: true }));

      var link = document.createElement("a");
      link.download = fileName;
      link.href = url;
      link.click();

      // Re-Enable the Save SVG button once done
      var fractalTreeApp = this;
      setTimeout(function () {
        fractalTreeApp.buttonSaveSVG.attr("value", "Save SVG to Device");
        fractalTreeApp.buttonSaveSVG.attr("disabled", false);
      }, 10);
    }
  },

  getAngle: function (distance, base) {
    return ((2 * Math.PI) / base) * distance;
  },
  getCartesianCoordinates: function (angle, radius) {
    return [Math.cos(angle) * radius, Math.sin(angle) * radius];
  },
  getLabelFontSize() {
    return Math.min(15, 5 + this.branchAngleMax / (2 * this.base));
  },
  formatDecimal: function (value, sample) {
    valueParsed = Number(value);
    sampleParsed = Number(sample);
    var decimalPortion = sampleParsed.toString().split(".")[1];
    var decimalPlaces = 0;
    if (decimalPortion) {
      decimalPlaces = decimalPortion.length;
    }
    var base = Math.pow(10, decimalPlaces);
    return Number(
      (Math.round(valueParsed * base) / base).toFixed(decimalPlaces)
    );
  },
  /**
   * Gets the rgb value array for the given recursion level. Calculates or retrieves the cached value.
   **/
  getRgb: function (level) {
    if (this.colorRgbMap[level] == null) {
      // Keep hue value in range [0, 1]
      var hue = (level / 10) % 1;
      var rgb = this.hslToRgb(hue, 0.5, 0.5);
      this.colorRgbMap[level] = rgb;
    }
    return this.colorRgbMap[level];
  },

  /**
   * Converts an HSL color value to RGB. Conversion formula
   * adapted from http://en.wikipedia.org/wiki/HSL_color_space.
   * Assumes h, s, and l are contained in the set [0, 1] and
   * returns r, g, and b in the set [0, 255].
   *
   * @param   {number}  h       The hue
   * @param   {number}  s       The saturation
   * @param   {number}  l       The lightness
   * @return  {Array}           The RGB representation
   */
  hslToRgb: function (h, s, l) {
    var r, g, b;

    if (s == 0) {
      r = g = b = l; // achromatic
    } else {
      var hue2rgb = function hue2rgb(p, q, t) {
        if (t < 0) t += 1;
        if (t > 1) t -= 1;
        if (t < 1 / 6) return p + (q - p) * 6 * t;
        if (t < 1 / 2) return q;
        if (t < 2 / 3) return p + (q - p) * (2 / 3 - t) * 6;
        return p;
      };

      var q = l < 0.5 ? l * (1 + s) : l + s - l * s;
      var p = 2 * l - q;
      r = hue2rgb(p, q, h + 1 / 3);
      g = hue2rgb(p, q, h);
      b = hue2rgb(p, q, h - 1 / 3);
    }

    return [Math.round(r * 255), Math.round(g * 255), Math.round(b * 255)];
  },
  drawLine: function (point0, point1) {
    var segment = new Path();
    segment.strokeWidth = 1;
    segment.add(point0);
    segment.add(point1);
    var rgb = this.getRgb(this.multiplyFactor);
    segment.strokeColor = new Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255);
    return segment;
  },
  drawContent: function () {
    this.iterations = 0;
    this.initialVector = new Point(0, -this.treeSize);

    var itemGroup = new Group();
    itemGroup = this.drawRecursion(
      itemGroup,
      this.initialPoint,
      this.initialVector,
      this.recursionLevels,
      this.numberBranches,
      this.branchAngle,
      this.lengthScale
    );
    return itemGroup;
  },
  drawRecursion: function (
    itemGroup,
    currentPoint,
    currentVector,
    recursionLevels,
    numberBranches,
    branchAngle,
    lengthScale
  ) {
    var currItemGroup = itemGroup;

    var nextPoint = new Point(
      currentPoint.x + currentVector.x,
      currentPoint.y + currentVector.y
    );

    if (this.iterations != 0 || this.drawTrunk) {
      // Draw new point
      var segment = new Path();
      segment.strokeWidth = Math.max(1, recursionLevels);
      segment.strokeCap = "round";
      segment.add(currentPoint);
      segment.add(nextPoint);
      var rgb = this.getRgb(recursionLevels);
      //	var rgb = this.getRgb(recursionLevels - this.recursionLevels);
      segment.strokeColor = new Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255);
      itemGroup.addChild(segment);
    }
    this.iterations++;

    var nextRecursionLevels = recursionLevels - 1;
    if (recursionLevels > 0) {
      var maxIterations =
        recursionLevels % this.spiralFactor == 0
          ? numberBranches * (this.spiralFactor + 1)
          : numberBranches;
      var iterationIncrement =
        recursionLevels % this.spiralFactor == 0 ? this.spiralFactor + 1 : 1;

      var i = 0;
      for (i = 0; i < maxIterations; i += iterationIncrement) {
        var angle = branchAngle * (1 / 2 + i - numberBranches / 2);

        var nextVector = currentVector.rotate(angle);
        nextVector.length /= lengthScale;
        this.drawRecursion(
          currItemGroup,
          nextPoint,
          nextVector,
          nextRecursionLevels,
          numberBranches,
          branchAngle,
          lengthScale
        );
      }
    } else {
      if (this.drawFruit) {
        var circle = new Path.Circle(
          nextPoint,
          Math.max(1, this.recursionLevelsMax - this.recursionLevels)
        );
        //	circle.strokeWidth = Math.max(1, recursionLevels);
        circle.strokeCap = "round";
        var rgb = this.getRgb(recursionLevels - this.recursionLevels - 1);
        circle.fillColor = new Color(rgb[0] / 255, rgb[1] / 255, rgb[2] / 255);
        itemGroup.addChild(circle);
      }
    }
    return currItemGroup;
  },
  update: function () {
    if (this.animateBranchAngle) {
      this.branchAngle = this.branchAngle + 1;
      fractalTreeApp.updateUIBranchAngle();
      if (this.branchAngle >= this.branchAngleMax) {
        this.branchAngle = this.branchAngleMin;
      }
      this.contentGroup = fractalTreeApp.redraw(
        fractalTreeApp.contentGroup,
        fractalTreeApp.drawContent()
      );
    }
  },

  redraw: function (drawGroup, drawFunction) {
    // Remove group and redraw
    if (drawGroup) {
      drawGroup.remove();
    }
    return drawFunction;
  },
  resize: function () {
    var height = Math.min(
      this.window.height(),
      this.controlsContainer.height()
    );
    var offset = this.animationContainer.offset().top;
    this.animationContainer.height(height);
  },
  start: function () {
    // Initialize Drawing
    this.contentGroup = fractalTreeApp.redraw(
      fractalTreeApp.contentGroup,
      fractalTreeApp.drawContent()
    );

    view.onFrame = function (event) {
      fractalTreeApp.update();
    };

    view.onResize = function (event) {
      fractalTreeApp.initView();
    };
  }
};

var fractalTreeApp;

$(function () {
  // Remove the placeholder image used for pen preview
  $("#tree-placeholder").remove();

  // Setup Paper.JS
  paper.install(window);
  fractalTreeApp = new Fractal_Tree();

  // Initialize fractalTreeApplication
  fractalTreeApp.initControls();
  fractalTreeApp.resize();
  paper.setup("canvas-fractal-tree");
  fractalTreeApp.initView();
  fractalTreeApp.start();
});

$(window).resize(function () {
  fractalTreeApp.initView();
});
