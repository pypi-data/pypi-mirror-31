(function($, _) {
  'use strict';

  // time between polls of responses API
  var POLLING_MILLIS = 3000;
  // time between timer rendering updates
  var TIMER_MILLIS = 1000;
  // color palette for bars
  var PALETTE = [
    '#1e73ae',
    '#dddb32',
    '#2b9b2b',
    '#e1516f',
    '#08cdf1',
    '#a964d4',
    '#505050',
    '#f77b0e',
    '#472ecc',
    '#7cce40',
    '#876a16'
  ];
  // this sentinel value means no data should be shown
  var NONE_SELECTION = 'None';

  function RapidResponseAsideView(runtime, element) {
    var toggleStatusUrl = runtime.handlerUrl(element, 'toggle_block_open_status');
    var responsesUrl = runtime.handlerUrl(element, 'responses');
    var $element = $(element);

    var rapidTopLevelSel = '.rapid-response-block';
    var rapidBlockControlsSel = '.rapid-response-controls';
    var rapidBlockResultsSel = '.rapid-response-results';
    var problemStatusBtnSel = '.problem-status-toggle';
    var buttonsRowSel = '.buttons-row';
    var timerSel = '.timer';
    var timerSpinnerSel = '.timer-spinner';
    var timerSpinnerTextSel = '.timer-spinner-text';
    var numStudentsSel = '.num-students';
    var tooltipContainerSel = '.rapid-response-tooltip-container';

    var tooltipTemplate = _.template(
      '<div class="rapid-response-tooltip">' +
      '<div class="tooltip-title"><%= title %></div>' +
      '<div class="tooltip-body">' +
      'Total: <span class="tooltip-total"><%= total %></span><br />' +
      'Percent: <span class="tooltip-percent"><%= percent %></span>' +
      '</div>' +
      '</div>'
    );
    // This will get attached to the beginning of <body /> on document load
    var $tooltipContainer;

    // default values
    var state = {
      is_open: false,
      runs: [],
      choices: [],
      counts: {},
      selectedRuns: [null],  // one per chart. null means select the latest one
      isFetchingResponses: false,  // is there a request in progress? Used to disable button to prevent double clicks
      lastFetch: null  // a moment object representing the time at last poll, to be used to diff with the run
    };

    /**
     * If there is an open problem, return a string showing how many people submitted a response for the open problem
     * and how many others who are enrolled.
     *
     * @param {number} runId The run to create the message for
     * @returns {string} The message
     */
    function makeNumStudentsMessage(runId) {
      var totalCount = state.total_counts[runId] || 0;

      var nounVerb = totalCount === 1 ? 'student has' : 'students have';

      return totalCount + ' ' + nounVerb + ' answered';
    }

    /**
     * Render template
     */
    function render() {
      renderControls();
      renderChartContainer();
    }

    // TODO: These values are guesses, maybe we want to calculate based on browser width/height? Not sure
    var ChartSettings = {
      top: 50, // space for text for upper label on y axis
      left: 50, // space for y axis
      right: 50, // space for text to flow
      bottom: 150, // space for x axis
      outerBufferWidth: 200, // pixels on the right and left
      outerTop: 100, // space between chart and top of container, should contain enough space for buttons
      innerBufferWidth: 0, // space between two charts
      numYAxisTicks: 6,
      minChartWidth: 400,
      maxChartWidth: 1300,
      minChartHeight: 500,
      maxChartHeight: 800
    };

    /**
     * Given the domain limits return some tick values, equally spaced out, all integers.
     * @param {number} domainMax The maximum domain value (the minimum is always 0).
     * @returns {Array} An array of integers within the domain used for tick values on the y axis
     */
    function makeIntegerTicks(domainMax) {
      var increment = Math.ceil(domainMax / ChartSettings.numYAxisTicks);
      return _.range(0, domainMax + 1, increment);
    }

    /**
     * Calculate width of a chart given the number of charts and the browser width
     *
     * @returns {number} Chart width in pixels
     */
    function calcChartWidth() {
      var browserWidth = $(window).width();
      var numCharts = state.selectedRuns.length;
      return Math.max(
        ChartSettings.minChartWidth,
        Math.min(
          ChartSettings.maxChartWidth,
          ((browserWidth - ChartSettings.outerBufferWidth) / numCharts) -
          (ChartSettings.innerBufferWidth * (numCharts - 1))
        )
      );
    }

    /**
     * Calculate height of a chart given the browser width
     *
     * @returns {number} Chart height in pixels
     */
    function calcChartHeight() {
      var browserHeight = $(window).height();
      return Math.max(
        ChartSettings.minChartHeight,
        Math.min(
          ChartSettings.maxChartHeight,
          browserHeight - ChartSettings.outerTop
        )
      );
    }

    /**
     * SVG doesn't have a capability to wrap text except for foreignObject which is not supported in IE11.
     * So we have to calculate it manually for X axis tick labels.
     * See https://bl.ocks.org/mbostock/7555321 for inspiration
     *
     * @param {selector} textSelector A D3 selector for x axis text elements
     * @param {number} barWidth The width of a bar
     * @param {string} text The text for the axis label
     */
    function wrapText(textSelector, barWidth, text) {
      textSelector.each(function() {
        // This is a g.tick item
        var root = d3.select(this);
        var rootText = root.select("text");

        var rootY = rootText.attr("y");
        var rootDy = parseFloat(rootText.attr("dy"));
        rootText.remove();
        root.select("g").remove();

        var angle = 30;
        var radians = angle * Math.PI / 180;
        // yay trig
        // this value is the maximum length for the text when laid out at an angle
        // hypotenuse is divided in half since text is starting in center
        var maxTextWidth = (barWidth / Math.cos(radians)) / 2;
        var rootContainer = root.append("g").attr("transform", "rotate(" + angle + ", 0, 10)");
        rootText = rootContainer.append("text")
          .attr("fill", "#000")
          .attr("text-anchor", "start")
          .attr("dy", rootDy + "em")
          .attr("y", rootY);

        var words = text.split(/\s+/);
        var tspan = rootText.append("tspan").attr("x", 0).attr("y", rootY).attr("dy", rootDy + "em");

        var currentLine = 0;
        var lineHeight = 1.1;
        // Build the text word by word so that it breaks lines appropriately
        // and cuts off with an ellipsis if it gets too long
        words.forEach(function(word) {
          // If the input text is empty or we have exceeded two lines
          // don't do anything
          if (!word || currentLine > 1) {
            return;
          }

          var compiledText = tspan.text();
          tspan.text(compiledText + " " + word);
          if (tspan.node().getComputedTextLength() > maxTextWidth) {
            // Check if the new word would go beyond the bar width boundary.

            // If this is the first word on the line we don't have a choice but to render it
            if (compiledText.length === 0) {
              return;
            }

            if (currentLine === 1) {
              // there is a maximum of two lines until we add the ellipses
              tspan.text(compiledText + "...");
              currentLine++;
              return;
            }

            // Change tspan back to its old text and create a one with the
            // word on a new line.
            currentLine++;
            tspan.text(compiledText + " ");
            tspan = rootText.append("tspan").attr("x", 0).attr("y", rootY).attr(
              "dy", ((currentLine * lineHeight) + rootDy) + "em"
            ).text(word);
          }
        });
      });
    }

    /**
     * Click handler to close this chart
     * @param {number} chartIndex The index of the chart
     */
    function closeChart(chartIndex) {
      state.selectedRuns.splice(chartIndex, 1);
      render();
    }

    /**
     * Select handler to choose a different run for the chart
     * @param {number} chartIndex The index of the chart
     */
    function changeSelectedChart(chartIndex) {
      var selectedRun = this.value;
      if (selectedRun !== NONE_SELECTION) {
        selectedRun = parseInt(selectedRun);
      }
      state.selectedRuns[chartIndex] = selectedRun;
      render();
    }

    /**
     * Click handler to open a new chart for comparison
     */
    function openNewChart() {
      state.selectedRuns = [state.selectedRuns[0], NONE_SELECTION];
      render();
    }

    /**
     * Renders the container elements for the charts using D3
     */
    function renderChartContainer() {
      // Get the indexes for selected runs. This should either be [0] or [0, 1].
      var chartKeys = _.keys(state.selectedRuns);

      // D3 data join for charts. Create a container div for each chart to store graph, select element and buttons.
      var containers = d3.select(element)
        .select(rapidBlockResultsSel)
        .selectAll(".chart-container")
        .data(chartKeys);
      var newContainers = containers.enter()
        .append("div");

      // chart selection, close and compare buttons
      var selectionContainers = containers.selectAll(".selection-container");
      var newSelectionContainers = newContainers
        .append("div")
        .classed("selection-container", true);

      newSelectionContainers.append("select")
        .on('change', changeSelectedChart);

      newSelectionContainers.append("a")
        .classed("compare-responses", true)
        .text("Compare responses")
        .on("click", openNewChart);

      newSelectionContainers.append("a")
        .classed("close", true)
        .text("Close")
        .on('click', closeChart);

      var selectionRowsMerged = newSelectionContainers.merge(selectionContainers)
        .attr("style", "margin-left: " + ChartSettings.left + "px");
      selectionRowsMerged.selectAll(".compare-responses").classed("hidden", function() {
        return chartKeys.length !== 1 || state.is_open || state.runs.length < 2;
      });
      selectionRowsMerged.selectAll(".close").classed("hidden", function() {
        return chartKeys.length === 1;
      });

      // create the chart svg container
      var newCharts = newContainers
        .append("svg")
        // The g element has a little bit of padding so the x and y axes can surround it
        .append("g").attr("class", "chart");
      // create x and y axes
      newCharts.append("g").attr("class", "xaxis");
      newCharts.append("g").attr("class", "yaxis");

      newContainers.merge(containers)
        .attr("class", "chart-container " + (chartKeys.length === 1 ? 'single-chart' : 'two-charts'))
        .each(function (index, __, charts) {
          renderChart(d3.select(charts[index]), index);
        })
        .selectAll("svg")
        .attr("width", calcChartWidth())
        .attr("height", calcChartHeight())
        .selectAll(".chart")
        .attr("transform", "translate(" + ChartSettings.left + "," + ChartSettings.top + ")")
        .select(".xaxis");

      // Remove charts if selectedRuns reduces in size.
      // We don't need to do this for all the inner elements, the remove will propagate.
      containers.exit().remove();
    }

    /**
     * Get a selected run id, or undefined if there are no runs
     *
     * @param {number} chartIndex Index of the chart
     * @returns {number} A run id
     */
    function getSelectedRun(chartIndex) {
      var runs = state.runs;
      var selectedRun = state.selectedRuns[chartIndex];

      if (selectedRun === null && runs.length > 0) {
        // The newest run should be the most recent one according to the info received from the server.
        selectedRun = runs[0].id;
      }

      return selectedRun;
    }

    /**
     * Render the chart in the container.
     *
     * @param {Object} container D3 selector for the chart container
     * @param {number} chartIndex The index of the chart (either 0 or 1)
     */
    function renderChart(container, chartIndex) {
      var runs = state.runs;
      var choices = state.choices;
      var counts = state.counts;
      var selectedRun = getSelectedRun(chartIndex);
      var totalCounts = state.total_counts;

      var histogram = choices.map(function (item) {
        return {
          answer_id: item.answer_id,
          answer_text: item.answer_text,
          count: counts[item.answer_id][selectedRun] || 0,
          total: totalCounts[selectedRun] || 0
        }
      });

      // select the proper option and use it to filter the runs
      var select = container.select(".selection-container").select("select")
        .classed("hidden", state.runs.length === 0 || state.is_open);

      // D3 data join on runs to create a select list
      var optionData = [{ id: NONE_SELECTION }].concat(runs);
      var options = select.selectAll("option").data(optionData, function(run) {
        return run.id;
      });
      options.enter()
        .append("option")
        .merge(options)
        .attr("value", function(run) { return run.id; })
        .text(function(run) {
          var totalCount = state.total_counts[run.id] || 0;

          if (run.id === NONE_SELECTION) {
            return (chartIndex > 0) ? 'Select' : 'None';
          }
          var dateString = moment(run.created).format("MMMM D, YYYY, h:mm:ss a");

          var noun = totalCount === 1 ? 'Response' : 'Responses';
          return dateString + " ------- " + totalCount + " " + noun;
        });
      options.exit().remove();

      select.enter().merge(select).property('value', selectedRun);

      // Compute responses into information suitable for a bar graph.
      var histogramAnswerIds = _.pluck(histogram, 'answer_id');
      var histogramLookup = _.object(_.map(histogram, function(item) {
        return [item.answer_id, item];
      }));

      // Create x scale to map answer ids to bar x coordinate locations. Note that
      // histogram was previously sorted in order of the lowercase answer id.
      var innerWidth = calcChartWidth() - ChartSettings.left - ChartSettings.right - ChartSettings.innerBufferWidth;
      var x = d3.scaleBand()
        .rangeRound([0, innerWidth])
        .padding(0.1)
        .domain(histogramAnswerIds);

      // Create y scale to map response count to y coordinate for the top of the bar.
      var innerHeight = calcChartHeight() - ChartSettings.top - ChartSettings.bottom;
      var yDomainMax = d3.max(choices, function(choice) {
        return d3.max(_.keys(state.selectedRuns), function(chartIndex) {
          var runId = getSelectedRun(chartIndex);
          return counts[choice.answer_id][runId] || 0;
        });
      });

      var y = d3.scaleLinear().rangeRound([innerHeight, 0]).domain(
        // pick the maximum count so we know how high the bar chart should go
        [0, yDomainMax]
      );
      // Create a color scale similar to the x scale to provide colors for each bar
      var color = d3.scaleOrdinal(PALETTE).domain(histogramAnswerIds);

      // The D3 data join. This matches the histogram data to the rect elements
      // (there is a __data__ attribute on each rect keeping track of this). Also tell D3 to use the answer_id to make
      // this match.
      var chart = container.select(".chart");
      var bars = chart.selectAll("rect").data(histogram, function(item) {
        return item.answer_id;
      });

      // Set the position and color attributes for the bars. Note that there is a transition applied
      // for the y axis for existing bars being updated.
      bars.enter()
        // Everything in between enter() and merge(bars) applies only to new bars. This creates a new rect.
        .append("rect").attr("class", "bar")
        // Set the height and y values according to the scale. This prevents weird transition behavior
        // where new bars appear to zap in out of nowhere.
        .attr("x", function(item) { return x(item.answer_id); })
        .attr("width", x.bandwidth())
        .attr("y", function(item) { return y(item.count); })
        .attr("height", function(item) {
          return innerHeight - y(item.count);
        })
        .on("mouseover", function(item) {
          var percent = '';
          if (item.total > 0) {
            // If there are no responses there should be no visible bars, but just in case
            percent = Math.round((item.count / item.total) * 100) + "%";
          }

          var templateState = {
            title: item.answer_text,
            total: item.count,
            percent: percent
          };
          $tooltipContainer.html(tooltipTemplate(templateState));
        })
        .on("mousemove", function() {
          $tooltipContainer.css("left", (d3.event.pageX + 20) + "px")
            .css("top", d3.event.pageY + "px");
        })
        .on("mouseout", function() {
          $tooltipContainer.html('');
        })
        .merge(bars)
        .attr("fill", function(item) {
          return color(item.answer_id);
        })
        .transition()
        // Set a transition for bars so that we have a slick update.
        .attr("x", function(item) { return x(item.answer_id); })
        .attr("width", x.bandwidth())
        .attr("y", function(item) { return y(item.count); })
        .attr("height", function(item) {
          return innerHeight - y(item.count);
        });

      // If the responses disappear from the API such that there is no information for the bar
      // (probably shouldn't happen),
      // remove the corresponding rect element.
      bars.exit().remove();

      // Update the X axis
      chart.select(".xaxis")
        .transition()
        .call(
          d3.axisBottom(x).tickFormat(function() {
            // Return null to output no text by default
            // The wrapText(...) call below will add text manually to let us adjust the angle and fit boundaries
            return null;
          })
        )
        .attr("transform", "translate(0," +
          (calcChartHeight() - ChartSettings.bottom - ChartSettings.top) +
        ")")
        .selectAll(".tick")
        .each(function(answerId, i, nodes) {
          var response = histogramLookup[answerId];
          var answerText = response ? response.answer_text : "";
          wrapText(d3.select(nodes[i]), x.bandwidth(), answerText);
        });

      // Update the Y axis.
      // By default it assumes a continuous scale, but we just want to show integers so we need to create the ticks
      // manually.
      var yTickValues = makeIntegerTicks(yDomainMax);
      chart.select(".yaxis")
        .transition() // transition to match the bar update
        .call(
          d3.axisLeft(y)
            .tickValues(yTickValues)
            .tickFormat(d3.format("d"))
            // make the tick stretch to cover the entire chart
            .tickSize(-innerWidth)
        )
        .selectAll(".tick")
        // render the tick line as a dashed line
        .attr("stroke-dasharray", function(value) {
          // At 0 the line should be solid to blend in with the chart border
          return value === 0 ? null : "8,8";
        })
        .selectAll("line")
        .attr("stroke", "rgba(0,0,0,.3)");

      // strangely, the default path has a line at the side and one at the top
      // we just want the one on the side
      chart.select(".yaxis .domain").remove();
      // Render a vertical line at x=0
      chart.select(".yaxis")
        .append("line")
        .classed("line", true)
        .attr("stroke", "#000")
        .attr("x2", 0.5);
      chart.select(".yaxis .line")
        .transition()
        .attr("y2", innerHeight);
    }

    /**
     * millis is the time between current time and the time of last fetch (according to browser), plus
     * the time between the last fetch and the run creation (according to server)
     * @returns {number}
     */
    function getSecondsSinceRunOpened() {
      if (state.runs.length === 0) {
        return 0;
      }
      var run = state.runs[0];
      if (!run.open) {
        return 0;
      }
      var millis = moment().diff(state.lastFetch) + moment(state.server_now).diff(moment(run.created));
      return Math.floor(millis / 1000);
    }

    /**
     * Render buttons and select element above the chart
     */
    function renderControls() {
      var $buttonsRow = $element.find(buttonsRowSel);
      var $problemButton = $element.find(problemStatusBtnSel);
      var $timer = $element.find(timerSel);
      var $timerSpinner = $element.find(timerSpinnerSel);
      var $timerSpinnerText = $element.find(timerSpinnerTextSel);
      var $numStudents = $element.find(numStudentsSel);

      if (state.selectedRuns.length !== 1) {
        // Don't show these buttons for the the compare view
        $buttonsRow.toggleClass('hidden', true);
        return;
      }

      $buttonsRow.toggleClass('hidden', false);
      $problemButton.text((state.is_open ? "Close" : "Open") + " Problem Now");

      var totalSeconds = getSecondsSinceRunOpened();
      var pollSeconds = 0, pollMinutes = 0;
      if (state.is_open) {
        pollSeconds = totalSeconds % 60;
        pollMinutes = Math.floor(totalSeconds / 60);
      }
      $timer.text(pollMinutes + "m : " + pollSeconds + "s");
      $timer.toggleClass("on", state.is_open);
      $timerSpinner.toggleClass('hidden', !state.is_open);
      $timerSpinnerText.toggleClass('hidden', !state.is_open);
      $numStudents.toggleClass('hidden', !state.is_open);

      // using chartIndex 0 since this message should only get shown if there is only one chart visible
      if (state.runs.length > 0 && state.is_open) {
        var numStudentsMessage = makeNumStudentsMessage(getSelectedRun(0));
        $numStudents.text(numStudentsMessage);
      }
    }

    /**
     * Update the timer every second
     */
    function updateTimer() {
      if (state.is_open) {
        setTimeout(updateTimer, TIMER_MILLIS);
      }
      renderControls();
    }

    /**
     * Poll responses API. If the problem is open, schedule another poll using this function.
     */
    function pollForResponses() {
      if (state.is_open) {
        setTimeout(pollForResponses, POLLING_MILLIS);
      }
      fetchResponsesAndRender();
    }

    /**
     * Read from the responses API and put the new value in the rendering state.
     */
    function fetchResponsesAndRender() {
      // make sure this updates at least once a second
      if (state.isFetchingResponses) {
        // API call is still in progress
        return;
      }

      state.isFetchingResponses = true;
      $.get(responsesUrl).then(function(newState) {
        _.assign(state, newState, {
          isFetchingResponses: false,
          lastFetch: moment()
        });
        render();
      });
    }

    $(function($) { // onLoad
      // there can be only one
      $tooltipContainer = $(tooltipContainerSel);
      if ($tooltipContainer.length === 0) {
        $tooltipContainer = $(
          '<div class="rapid-response-tooltip-container"></div>'
        );
        $("body").prepend($tooltipContainer);
      }

      var block = $element.find(rapidTopLevelSel);
      state.is_open = block.attr('data-open') === 'True';

      var $rapidBlockContent = $element.find(rapidBlockControlsSel);

      var linkIsDisabled = false;

      $rapidBlockContent.find(problemStatusBtnSel).click(function() {
        if (linkIsDisabled) {
          return;
        }

        // disable the button temporarily to prevent double clicks
        linkIsDisabled = true;
        $rapidBlockContent.find(problemStatusBtnSel).toggleClass("disabled", true);
        $.post(toggleStatusUrl).then(
          function(newState) {
            linkIsDisabled = false;
            $rapidBlockContent.find(problemStatusBtnSel).toggleClass("disabled", false);

            // Selected runs should be reset when the open status is changed
            _.assign(state, newState, {
              selectedRuns: [null]
            });

            renderControls();
            if (state.is_open) {
              pollForResponses();
              updateTimer();
            } else {
              fetchResponsesAndRender();
            }
          }
        );
      });

      // This contains the staff-only buttons
      var $wrapInstructorInfo = $element.parent().find(".wrap-instructor-info");
      if ($wrapInstructorInfo.length) {
        // The BR element will clear the floats via the CSS rule
        $wrapInstructorInfo.append($("<br />"));
      }

      renderControls();
      fetchResponsesAndRender();

      // adjust graph for each rerender
      window.addEventListener('resize', function() {
        render();
      });

      if (state.is_open) {
        pollForResponses();
        updateTimer();
      }
    });
  }

  function initializeRapidResponseAside(runtime, element) {
    return new RapidResponseAsideView(runtime, element);
  }

  window.RapidResponseAsideInit = initializeRapidResponseAside;
}($, _));
