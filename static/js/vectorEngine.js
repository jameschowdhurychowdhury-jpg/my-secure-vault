/**
 * =========================================================================
 * SHATTERED REALM PROCEDURAL VECTOR ENGINE
 * SYSTEM CODE CONTEXT FRAMEWORK V2.12 - COMPLETE CYLINDER INTEGRITY PATCH
 * =========================================================================
 */

(function () {
    'use strict';

    // Core Canvas Infrastructure Handlers
    const canvas = document.getElementById('masterRenderCanvas');
    const ctx = canvas.getContext('2d');
    const uprockWidget = document.getElementById('interactiveUprockRegion');
    const gateViewport = document.getElementById('gateViewport');
    const guideText = document.getElementById('systemGuideText');
    const magmaTele = document.getElementById('magmaTelemetryValue');
    const qiTele = document.getElementById('qiResonanceValue');
    const hexNodeCore = document.getElementById('hexNodeCore');

    let width = canvas.width = window.innerWidth;
    let height = canvas.height = window.innerHeight;

    // Operational Framework Animation State Flags
    let frameCounter = 0;
    let portalSummoned = false;
    let portalTransitionProgress = 0;
    
    // Interaction Tracking Data Points
    let userMouse = { x: -1000, y: -1000, targetX: -1000, targetY: -1000, trackingActive: false };
    
    // 3D Cylinder Rotation Management Vectors
    let isDragging = false;
    let previousMouseX = 0;
    let rotationY = 0;
    let targetRotationY = 0;
    let rotationX = -12; // Static downward angular tilt matching blueprint file

    // Procedural Landscape Structural Data Containers
    let ridgeLayerBack = [];
    let ridgeLayerFront = [];
    let geologicalRocks = [];
    let structuralWeapons = [];
    let atmosphericAshes = [];
    let volumetricSmoke = [];
    let fluidLavaBubbles = [];

    // Static Asset Simulation Definitions
    let fallenInterfacePlate = { x: 0, y: 0, w: 180, h: 44, staticAngle: 16.5 };
    let uprockSystemAnchor = { x: 0, y: 0, screenX: 0, screenY: 0, oscillationDelta: 0 };

    /**
     * Mathematical Pseudo-Random Noise Map Module
     */
    const TerrainNoiseGenerator = {
        seedValue: 0.74239104,
        extractNoise: function (x) {
            let chunk = Math.sin(x * 12.9898 + this.seedValue) * 43758.5453123;
            return chunk - Math.floor(chunk);
        },
        evaluateSmoothNoise: function(x) {
            let base = Math.floor(x);
            let fractional = x - base;
            let smoothFactor = fractional * fractional * (3.0 - 2.0 * fractional);
            return this.extractNoise(base) * (1.0 - smoothFactor) + this.extractNoise(base + 1) * smoothFactor;
        },
        evaluateFractalOctaves: function(x, octavesCount) {
            let aggregate = 0;
            let scaleFrequency = 1.0;
            let amplitudeFactor = 1.0;
            let maxPotentialValue = 0;

            for(let i = 0; i < octavesCount; i++) {
                aggregate += this.evaluateSmoothNoise(x * scaleFrequency) * amplitudeFactor;
                maxPotentialValue += amplitudeFactor;
                amplitudeFactor *= 0.5;
                scaleFrequency *= 2.0;
            }
            return aggregate / maxPotentialValue;
        }
    };

    /**
     * Initialization Matrix Phase: Structures All Landscape Layers
     */
    function buildRealmSystemGeometry() {
        width = canvas.width = window.innerWidth;
        height = canvas.height = window.innerHeight;

        uprockSystemAnchor.screenX = width * 0.82;
        uprockSystemAnchor.screenY = height * 0.28;
        uprockSystemAnchor.x = uprockSystemAnchor.screenX;
        uprockSystemAnchor.y = uprockSystemAnchor.screenY;

        if (uprockWidget) {
            uprockWidget.style.left = `${uprockSystemAnchor.screenX}px`;
            uprockWidget.style.top = `${uprockSystemAnchor.screenY}px`;
        }

        fallenInterfacePlate.x = width * 0.64;
        fallenInterfacePlate.y = height - 68;

        ridgeLayerBack = [];
        ridgeLayerFront = [];
        geologicalRocks = [];
        structuralWeapons = [];

        // Background Mountain Ridgelines
        const backSegmentsCount = 40;
        for (let i = 0; i <= backSegmentsCount; i++) {
            let sampleX = (width / backSegmentsCount) * i;
            let noiseInputValue = (i * 0.15) + 4.5;
            let noiseOutput = TerrainNoiseGenerator.evaluateFractalOctaves(noiseInputValue, 3);
            
            let baselineElevation = height * 0.58;
            if(i < backSegmentsCount * 0.45) {
                baselineElevation -= (1.0 - (i / (backSegmentsCount * 0.45))) * (height * 0.25);
            }
            ridgeLayerBack.push({ x: sampleX, y: baselineElevation + (noiseOutput * 90 - 45) });
        }

        // Foreground Obsidian Mountain Ridge Cliffs
        const frontSegmentsCount = 55;
        for (let i = 0; i <= frontSegmentsCount; i++) {
            let sampleX = (width / frontSegmentsCount) * i;
            let noiseInputValue = (i * 0.22) + 18.91;
            let noiseOutput = TerrainNoiseGenerator.evaluateFractalOctaves(noiseInputValue, 4);
            
            let baselineElevation = height * 0.74;
            if(i < frontSegmentsCount * 0.38) {
                baselineElevation -= (1.0 - (i / (frontSegmentsCount * 0.38))) * (height * 0.24);
            } else if (i > frontSegmentsCount * 0.78) {
                baselineElevation -= ((i - frontSegmentsCount * 0.78) / (frontSegmentsCount * 0.22)) * (height * 0.16);
            }
            ridgeLayerFront.push({ x: sampleX, y: baselineElevation + (noiseOutput * 110 - 55) });
        }

        // Populate High Density Geological Crags
        const totalRocksToDeploy = 55;
        for(let i = 0; i < totalRocksToDeploy; i++) {
            let deployedX = Math.random() * width;
            let underlyingTerrainY = evaluateTerrainHeightMetrics(deployedX, ridgeLayerFront);
            let deployedY = underlyingTerrainY + (Math.random() * 30 - 12);
            let computedRadius = Math.random() * 32 + 10;
            
            let polyVertices = [];
            let facetSidesCount = Math.floor(Math.random() * 4) + 5;
            for(let f = 0; f < facetSidesCount; f++) {
                let currentFacetAngle = (f / facetSidesCount) * Math.PI * 2;
                let irregularScalingRadius = computedRadius * (0.72 + Math.random() * 0.42);
                polyVertices.push({
                    dx: Math.cos(currentFacetAngle) * irregularScalingRadius,
                    dy: Math.sin(currentFacetAngle) * irregularScalingRadius
                });
            }

            geologicalRocks.push({
                x: deployedX, y: deployedY,
                vertices: polyVertices,
                grayLuminanceTone: Math.floor(Math.random() * 14) + 8,
                depthScaleMultiplier: Math.random() * 0.35 + 0.82
            });
        }

        // Populate Multi-Blade Structural Graveyard Arrays
        const weaponCountTarget = 44;
        for(let i = 0; i < weaponCountTarget; i++) {
            let weaponPlacementX = Math.random() * width;
            
            if(weaponPlacementX > width * 0.35 && weaponPlacementX < width * 0.65 && Math.random() * 100 > 20) {
                weaponPlacementX = Math.random() * 100 > 50 ? weaponPlacementX + (width * 0.22) : weaponPlacementX - (width * 0.22);
            }

            let landBaseY = evaluateTerrainHeightMetrics(weaponPlacementX, ridgeLayerFront);
            let standardBladeSize = Math.random() * 85 + 60;
            let handleHiltRatio = standardBladeSize * (0.24 + Math.random() * 0.08);
            let guardWidthProfile = Math.random() * 16 + 14;
            let structuralInclinationAngle = (Math.random() - 0.5) * 75;
            let absorptionDepthOffset = Math.random() * 25 + 22;

            structuralWeapons.push({
                x: weaponPlacementX,
                y: landBaseY + absorptionDepthOffset,
                bladeLength: standardBladeSize,
                hiltSize: handleHiltRatio,
                crossguardWidth: guardWidthProfile,
                tiltAngle: structuralInclinationAngle,
                bladeThickness: Math.random() * 4 + 4.5,
                runicEnergyIntensity: Math.random() * 0.65 + 0.35,
                isShatteredBladeArtifact: Math.random() * 100 > 75,
                renderInForegroundStack: Math.random() * 100 > 48
            });
        }

        structuralWeapons.sort((primary, secondary) => primary.y - secondary.y);

        // Build Atmospheric Particle Clusters
        atmosphericAshes = [];
        for(let i = 0; i < 110; i++) {
            atmosphericAshes.push({
                x: Math.random() * width,
                y: Math.random() * height,
                driftVelX: (Math.random() - 0.5) * 1.5,
                riseVelY: -(Math.random() * 2.2 + 0.6),
                particleRad: Math.random() * 2.2 + 0.8,
                clampedAlphaLimit: Math.random() * 0.65 + 0.25,
                alphaValue: 0,
                oscillationFrequencyPhase: Math.random() * Math.PI
            });
        }

        // Build Volumetric Smoke Simulation Clouds
        volumetricSmoke = [];
        for(let i = 0; i < 7; i++) {
            volumetricSmoke.push({
                x: width * (0.14 * i + 0.08),
                y: height * 0.45 + (Math.random() * 60 - 30),
                radius: 140 + i * 35,
                sinOffsetModifier: Math.random() * Math.PI * 2,
                velocityStep: Math.random() * 0.006 + 0.003
            });
        }

        // Build Fluid Lava Pool
        fluidLavaBubbles = [];
        for(let i = 0; i < 18; i++) {
            fluidLavaBubbles.push({
                x: Math.random() * width,
                y: height + Math.random() * 25,
                targetRadius: Math.random() * 22 + 6,
                boilSpeedFrequency: Math.random() * 0.035 + 0.015,
                runningPhaseRadian: Math.random() * Math.PI * 2
            });
        }
    }

    function evaluateTerrainHeightMetrics(targetCoordinatesX, targetRidgeArray) {
        if (targetRidgeArray.length === 0) return height * 0.75;
        if (targetCoordinatesX <= targetRidgeArray[0].x) return targetRidgeArray[0].y;
        if (targetCoordinatesX >= targetRidgeArray[targetRidgeArray.length - 1].x) return targetRidgeArray[targetRidgeArray.length - 1].y;

        for (let i = 0; i < targetRidgeArray.length - 1; i++) {
            if (targetCoordinatesX >= targetRidgeArray[i].x && targetCoordinatesX <= targetRidgeArray[i + 1].x) {
                let bindingLeftNode = targetRidgeArray[i];
                let bindingRightNode = targetRidgeArray[i + 1];
                let localInterpolationFactor = (targetCoordinatesX - bindingLeftNode.x) / (bindingRightNode.x - bindingLeftNode.x);
                return bindingLeftNode.y + localInterpolationFactor * (bindingRightNode.y - bindingLeftNode.y);
            }
        }
        return height * 0.75;
    }

    window.engagePortalSummonSequence = function() {
        if(portalSummoned) return;
        
        portalSummoned = true;
        if (gateViewport) gateViewport.classList.add('summoned');
        if (guideText) guideText.innerText = "MATRIX INTEGRATED // DRAG BACKGROUND TO REVOLVE HOLLOW COLUMN NODES";

        for (let i = 0; i < atmosphericAshes.length; i++) {
            let ash = atmosphericAshes[i];
            let deltaVectorX = ash.x - uprockSystemAnchor.x;
            let deltaVectorY = ash.y - uprockSystemAnchor.y;
            let computedDistanceValue = Math.sqrt(deltaVectorX * deltaVectorX + deltaVectorY * deltaVectorY);
            
            if(computedDistanceValue < 400) {
                ash.driftVelX = (deltaVectorX / computedDistanceValue) * 14;
                ash.riseVelY = (deltaVectorY / computedDistanceValue) * 14;
                ash.alphaValue = 1.0;
            }
        }
    };

    function pipelineRenderSmokeClouds() {
        ctx.save();
        for(let i = 0; i < volumetricSmoke.length; i++) {
            let smoke = volumetricSmoke[i];
            smoke.sinOffsetModifier += smoke.velocityStep;
            
            let dynamicPlumeX = smoke.x + Math.sin(smoke.sinOffsetModifier) * 50;
            let dynamicPlumeY = smoke.y + Math.cos(smoke.sinOffsetModifier * 0.8) * 15;

            let cloudGradientShader = ctx.createRadialGradient(
                dynamicPlumeX, dynamicPlumeY, 5, 
                dynamicPlumeX, dynamicPlumeY, smoke.radius
            );
            cloudGradientShader.addColorStop(0, 'rgba(8, 24, 38, 0.12)');
            cloudGradientShader.addColorStop(0.4, 'rgba(4, 12, 20, 0.05)');
            cloudGradientShader.addColorStop(1, 'rgba(0, 0, 0, 0)');

            ctx.beginPath();
            ctx.arc(dynamicPlumeX, dynamicPlumeY, smoke.radius, 0, Math.PI * 2);
            ctx.fillStyle = cloudGradientShader;
            ctx.fill();
        }
        ctx.restore();
    }

    function pipelineRenderSolidRocks(processForegroundStackOnly) {
        for(let i = 0; i < geologicalRocks.length; i++) {
            let cragRock = geologicalRocks[i];
            
            if(processForegroundStackOnly && cragRock.depthScaleMultiplier < 1.0) continue;
            if(!processForegroundStackOnly && cragRock.depthScaleMultiplier >= 1.0) continue;

            ctx.save();
            ctx.translate(cragRock.x, cragRock.y);
            ctx.scale(cragRock.depthScaleMultiplier, cragRock.depthScaleMultiplier);

            ctx.beginPath();
            ctx.moveTo(cragRock.vertices[0].dx, cragRock.vertices[0].dy);
            for(let v = 1; v < cragRock.vertices.length; v++) {
                ctx.lineTo(cragRock.vertices[v].dx, cragRock.vertices[v].dy);
            }
            ctx.closePath();

            let surfaceToneVal = cragRock.grayLuminanceTone;
            if(processForegroundStackOnly) surfaceToneVal -= 2;

            let lavaProximityInterpolation = Math.min(Math.max((height - cragRock.y) / 200, 0), 1);
            
            let rockGradientFillProfile = ctx.createLinearGradient(0, -35, 0, 35);
            rockGradientFillProfile.addColorStop(0, `rgb(${surfaceToneVal}, ${Math.floor(surfaceToneVal * 0.5)}, ${Math.floor(surfaceToneVal * 0.6)})`);
            rockGradientFillProfile.addColorStop(1, `rgb(2, ${Math.floor(surfaceToneVal * 0.2)}, ${surfaceToneVal + 20 + Math.floor((1.0 - lavaProximityInterpolation) * 30)})`);

            ctx.fillStyle = rockGradientFillProfile;
            ctx.fill();

            ctx.lineWidth = 1.0;
            ctx.strokeStyle = `rgba(0, 243, 255, ${0.12 + (1.0 - lavaProximityInterpolation) * 0.3})`;
            ctx.stroke();

            ctx.restore();
        }
    }

    function pipelineRenderWeaponGraveyard(processForegroundStackOnly) {
        for(let i = 0; i < structuralWeapons.length; i++) {
            let weapon = structuralWeapons[i];
            
            if(processForegroundStackOnly && !weapon.renderInForegroundStack) continue;
            if(!processForegroundStackOnly && weapon.renderInForegroundStack) continue;

            ctx.save();
            ctx.translate(weapon.x, weapon.y);
            ctx.rotate(weapon.tiltAngle * Math.PI / 180);

            let bladeTipY = -weapon.bladeLength;
            let bladeBaseY = -weapon.hiltSize;
            let gripTopY = -weapon.hiltSize;
            let gripBottomY = 0;
            let halfBladeWidth = weapon.bladeThickness * 0.5;
            let guardProfileHeight = weapon.bladeThickness * 0.9;

            ctx.beginPath();
            if(weapon.isShatteredBladeArtifact) {
                ctx.moveTo(-halfBladeWidth, bladeBaseY);
                ctx.lineTo(-halfBladeWidth, bladeTipY * 0.52);
                ctx.lineTo(halfBladeWidth * 0.25, bladeTipY * 0.46);
                ctx.lineTo(-halfBladeWidth * 0.35, bladeTipY * 0.38);
                ctx.lineTo(halfBladeWidth, bladeTipY * 0.32);
                ctx.lineTo(halfBladeWidth, bladeBaseY);
            } else {
                ctx.moveTo(-halfBladeWidth, bladeBaseY);
                ctx.lineTo(-halfBladeWidth * 0.85, bladeTipY * 0.93);
                ctx.lineTo(0, bladeTipY);
                ctx.lineTo(halfBladeWidth * 0.85, bladeTipY * 0.93);
                ctx.lineTo(halfBladeWidth, bladeBaseY);
            }
            ctx.closePath();

            let baseSteelToneIndex = weapon.renderInForegroundStack ? 26 : 16;
            let metallicSheenShader = ctx.createLinearGradient(-halfBladeWidth, 0, halfBladeWidth, 0);
            metallicSheenShader.addColorStop(0, `rgb(${baseSteelToneIndex}, ${baseSteelToneIndex + 4}, ${baseSteelToneIndex + 12})`);
            metallicSheenShader.addColorStop(0.5, `rgb(${baseSteelToneIndex + 10}, ${baseSteelToneIndex + 18}, ${baseSteelToneIndex + 28})`);
            metallicSheenShader.addColorStop(1, `rgb(${baseSteelToneIndex - 4}, ${baseSteelToneIndex - 2}, ${baseSteelToneIndex})`);

            ctx.fillStyle = metallicSheenShader;
            ctx.fill();

            let runningEnergyPulseAlpha = (Math.sin(frameCounter * 0.045 + i) * 0.28 + 0.72) * weapon.runicEnergyIntensity;
            ctx.beginPath();
            ctx.moveTo(0, bladeBaseY - 2);
            ctx.lineTo(0, weapon.isShatteredBladeArtifact ? bladeTipY * 0.28 : bladeTipY * 0.85);
            ctx.strokeStyle = `rgba(0, 243, 255, ${runningEnergyPulseAlpha})`;
            ctx.lineWidth = weapon.bladeThickness * 0.25;
            ctx.shadowBlur = 10;
            ctx.shadowColor = "rgba(0,180,255,1)";
            ctx.stroke();
            ctx.shadowBlur = 0;

            ctx.beginPath();
            ctx.rect(-weapon.crossguardWidth * 0.5, bladeBaseY - guardProfileHeight, weapon.crossguardWidth, guardProfileHeight);
            let castingBronzeTone = Math.floor(baseSteelToneIndex * 0.7);
            ctx.fillStyle = `rgb(2, ${castingBronzeTone + 6}, ${castingBronzeTone + 16})`;
            ctx.fill();
            ctx.strokeStyle = '#010203';
            ctx.lineWidth = 0.7;
            ctx.stroke();

            ctx.beginPath();
            ctx.rect(-halfBladeWidth * 0.65, gripTopY, halfBladeWidth * 1.3, gripBottomY - gripTopY);
            ctx.fillStyle = '#0a0c14';
            ctx.fill();

            ctx.beginPath();
            ctx.arc(0, gripBottomY + halfBladeWidth, halfBladeWidth * 1.25, 0, Math.PI * 2);
            ctx.fillStyle = `rgb(${baseSteelToneIndex + 4}, ${baseSteelToneIndex + 8}, ${baseSteelToneIndex + 14})`;
            ctx.fill();

            ctx.restore();
        }
    }

    function pipelineRenderFallenButtonMesh() {
        ctx.save();
        ctx.translate(fallenInterfacePlate.x, fallenInterfacePlate.y);
        ctx.rotate(fallenInterfacePlate.staticAngle * Math.PI / 180);

        let pw = fallenInterfacePlate.w;
        let ph = fallenInterfacePlate.h;

        ctx.beginPath();
        ctx.moveTo(0, 0);
        ctx.lineTo(pw * 0.32, ph * 0.15);
        ctx.lineTo(pw * 0.38, -ph * 0.05);
        ctx.lineTo(pw * 0.70, ph * 0.04);
        ctx.lineTo(pw * 0.65, ph * 0.25);
        ctx.lineTo(pw, ph * 0.20);
        ctx.lineTo(pw * 0.94, ph);
        ctx.lineTo(pw * 0.42, ph * 0.96);
        ctx.lineTo(pw * 0.38, ph * 1.15);
        ctx.lineTo(pw * 0.10, ph * 0.92);
        ctx.lineTo(-pw * 0.02, ph * 0.60);
        ctx.closePath();

        ctx.fillStyle = 'rgba(8, 14, 20, 0.9)';
        ctx.strokeStyle = '#112533';
        ctx.lineWidth = 1.5;
        ctx.fill();
        ctx.stroke();

        ctx.beginPath();
        ctx.moveTo(pw * 0.4, 0); ctx.lineTo(pw * 0.48, ph);
        ctx.moveTo(0, ph * 0.48); ctx.lineTo(pw * 0.75, ph * 0.38);
        ctx.strokeStyle = '#010105';
        ctx.lineWidth = 2.0;
        ctx.stroke();

        ctx.fillStyle = 'rgba(40, 56, 74, 0.4)';
        ctx.font = 'bold 10px monospace';
        ctx.textAlign = 'center';
        ctx.textBaseline = 'middle';
        ctx.fillText("LOGIN_GATE_NULL", pw * 0.5, ph * 0.5);

        ctx.restore();
    }

    function pipelineRenderViscousMagmaOcean() {
        let poolTopBaselineY = height - 52;
        
        ctx.beginPath();
        ctx.moveTo(0, height);
        ctx.lineTo(0, poolTopBaselineY);
        
        const computingLiquidResolutionNodes = 16;
        for(let i = 0; i <= computingLiquidResolutionNodes; i++) {
            let horizontalNodeX = (width / computingLiquidResolutionNodes) * i;
            let localizedWaveOffsetHeight = Math.sin(frameCounter * 0.03 + i * 0.9) * 5.5;
            ctx.lineTo(horizontalNodeX, poolTopBaselineY + localizedWaveOffsetHeight);
        }
        ctx.lineTo(width, height);
        ctx.closePath();

        let liquidCoreGradientShader = ctx.createLinearGradient(0, poolTopBaselineY - 15, 0, height);
        liquidCoreGradientShader.addColorStop(0, 'rgba(0, 162, 255, 0.98)');
        liquidCoreGradientShader.addColorStop(0.25, 'rgba(0, 80, 255, 1)');
        liquidCoreGradientShader.addColorStop(0.65, 'rgba(0, 20, 120, 1)');
        liquidCoreGradientShader.addColorStop(1, '#000205');
        
        ctx.fillStyle = liquidCoreGradientShader;
        ctx.fill();

        for(let i = 0; i < fluidLavaBubbles.length; i++) {
            let bubble = fluidLavaBubbles[i];
            bubble.runningPhaseRadian += bubble.boilSpeedFrequency;
            
            let bubbleCurrentY = (height - 32) + Math.sin(bubble.runningPhaseRadian) * 14;
            let scalingRadiusFactor = bubble.targetRadius * (0.88 + Math.cos(bubble.runningPhaseRadian * 1.4) * 0.12);

            ctx.beginPath();
            ctx.arc(bubble.x, bubbleCurrentY, scalingRadiusFactor, 0, Math.PI * 2);
            ctx.fillStyle = 'rgba(0, 120, 255, 0.22)';
            ctx.strokeStyle = 'rgba(0, 243, 255, 0.4)';
            ctx.lineWidth = 1.0;
            ctx.fill();
            ctx.stroke();

            if(bubble.runningPhaseRadian > Math.PI * 4) {
                bubble.x = Math.random() * width;
                bubble.runningPhaseRadian = 0;
            }
        }

        ctx.beginPath();
        ctx.moveTo(0, poolTopBaselineY + Math.sin(frameCounter * 0.03) * 5.5);
        for(let i = 0; i <= computingLiquidResolutionNodes; i++) {
            let horizontalNodeX = (width / computingLiquidResolutionNodes) * i;
            let localizedWaveOffsetHeight = Math.sin(frameCounter * 0.03 + i * 0.9) * 5.5;
            ctx.lineTo(horizontalNodeX, poolTopBaselineY + localizedWaveOffsetHeight);
        }
        ctx.strokeStyle = 'rgba(150, 225, 255, 0.85)';
        ctx.lineWidth = 1.5;
        ctx.shadowBlur = 14;
        ctx.shadowColor = "rgba(0,120,255,1)";
        ctx.stroke();
        ctx.shadowBlur = 0;
    }

    function pipelineRenderAshSystem() {
        for(let i = 0; i < atmosphericAshes.length; i++) {
            let ashParticle = atmosphericAshes[i];
            ashParticle.x += ashParticle.driftVelX;
            ashParticle.y += ashParticle.riseVelY;
            ashParticle.oscillationFrequencyPhase += 0.035;

            if(portalSummoned) {
                ashParticle.driftVelX *= 0.96;
                ashParticle.riseVelY = ashParticle.riseVelY * 0.96 + (-1.4 * 0.04);
            }

            let computedTargetAlpha = Math.max(0, ashParticle.clampedAlphaLimit * (0.55 + Math.sin(ashParticle.oscillationFrequencyPhase) * 0.45));
            if(ashParticle.alphaValue < computedTargetAlpha) {
                ashParticle.alphaValue += 0.015;
            } else {
                ashParticle.alphaValue = computedTargetAlpha;
            }

            if(userMouse.trackingActive) {
                let dx = userMouse.x - ashParticle.x;
                let dy = userMouse.y - ashParticle.y;
                let dist = Math.sqrt(dx * dx + dy * dy);
                if(dist < 180) {
                    let forceFactor = (1.0 - (dist / 180)) * 0.8;
                    ashParticle.x -= (dx / dist) * forceFactor;
                    ashParticle.y -= (dy / dist) * forceFactor;
                }
            }

            ctx.beginPath();
            ctx.arc(ashParticle.x, ashParticle.y, ashParticle.particleRad, 0, Math.PI * 2);
            
            let emissionGreenChannel = Math.floor(100 + (ashParticle.y / height) * 120);
            ctx.fillStyle = `rgba(15, ${emissionGreenChannel}, 255, ${ashParticle.alphaValue})`;
            
            ctx.shadowBlur = ashParticle.particleRad * 2.0;
            ctx.shadowColor = "rgba(0,162,255,0.7)";
            ctx.fill();
            ctx.shadowBlur = 0;

            if (ashParticle.y < -10 || ashParticle.x < -10 || ashParticle.x > width + 10) {
                ashParticle.x = Math.random() * width;
                ashParticle.y = height + Math.random() * 25;
                ashParticle.driftVelX = (Math.random() - 0.5) * 1.5;
                ashParticle.riseVelY = -(Math.random() * 2.2 + 0.6);
                ashParticle.alphaValue = 0;
            }
        }
    }

    function pipelineRenderEnergyConduits(currentUprockFloatingY) {
        let formationTargetX = width * 0.5;
        let formationTargetY = height * 0.48;

        ctx.save();
        ctx.beginPath();
        ctx.ellipse(formationTargetX, formationTargetY, 200 * portalTransitionProgress, 260 * portalTransitionProgress, Math.sin(frameCounter * 0.008) * 0.04, 0, Math.PI * 2);
        ctx.strokeStyle = `rgba(2, 162, 255, ${0.32 * portalTransitionProgress})`;
        ctx.lineWidth = 4;
        ctx.shadowBlur = 30;
        ctx.shadowColor = "rgba(0,80,255,0.85)";
        ctx.stroke();
        ctx.shadowBlur = 0;
        ctx.restore();

        if(frameCounter % 7 === 0 || frameCounter % 11 === 0) {
            ctx.beginPath();
            ctx.moveTo(uprockSystemAnchor.x, currentUprockFloatingY);
            
            const fractalStepsCount = 7;
            for(let i = 1; i <= fractalStepsCount; i++) {
                let advancementRatio = i / fractalStepsCount;
                let nextTargetNodeX = uprockSystemAnchor.x + (formationTargetX - uprockSystemAnchor.x) * advancementRatio;
                let nextTargetNodeY = currentUprockFloatingY + (formationTargetY - currentUprockFloatingY) * advancementRatio;

                if(i < fractalStepsCount) {
                    nextTargetNodeX += (Math.random() - 0.5) * 38;
                    nextTargetNodeY += (Math.random() - 0.5) * 38;
                }

                ctx.lineTo(nextTargetNodeX, nextTargetNodeY);
            }

            ctx.strokeStyle = `rgba(150, 240, 255, ${0.72 * portalTransitionProgress})`;
            ctx.lineWidth = 1.3;
            ctx.shadowBlur = 12;
            ctx.shadowColor = "#00a2ff";
            ctx.stroke();
            ctx.shadowBlur = 0;
        }
    }

    /**
     * Master Engine Clock Runtime Animation Frame Pipeline Loop Tick
     */
    function executeMasterEnginePipelineTick() {
        frameCounter++;

        if (frameCounter % 15 === 0) {
            let dynamicMagmaMetric = (73.77 + Math.sin(frameCounter * 0.05) * 0.45).toFixed(2);
            let dynamicQiMetric = (1.0000 + Math.cos(frameCounter * 0.02) * 0.15 * portalTransitionProgress).toFixed(4);
            if (magmaTele) magmaTele.innerText = `DYNAMIC_${dynamicMagmaMetric}_RADS`;
            if (qiTele) qiTele.innerText = `${dynamicQiMetric}_hz`;
        }

        ctx.clearRect(0, 0, width, height);

        userMouse.x += (userMouse.targetX - userMouse.x) * 0.08;
        userMouse.y += (userMouse.targetY - userMouse.y) * 0.08;

        // Inertial rotation calculation pass
        rotationY += (targetRotationY - rotationY) * 0.1;
        if(portalSummoned && hexNodeCore) {
            hexNodeCore.style.transform = `rotateX(${rotationX}deg) rotateY(${rotationY}deg)`;
        }

        if(portalSummoned && portalTransitionProgress < 1.0) {
            portalTransitionProgress += 0.02;
            if(portalTransitionProgress > 1.0) portalTransitionProgress = 1.0;
        }

        uprockSystemAnchor.oscillationDelta = Math.sin(frameCounter * 0.022) * 12.5;
        let runningUprockFrameY = uprockSystemAnchor.y + uprockSystemAnchor.oscillationDelta;
        if (uprockWidget) uprockWidget.style.top = `${runningUprockFrameY}px`;

        pipelineRenderSmokeClouds();

        // Background Ridge
        ctx.beginPath();
        if (ridgeLayerBack.length > 0) {
            ctx.moveTo(0, height);
            ctx.lineTo(ridgeLayerBack[0].x, ridgeLayerBack[0].y);
            for (let i = 1; i < ridgeLayerBack.length; i++) {
                ctx.lineTo(ridgeLayerBack[i].x, ridgeLayerBack[i].y);
            }
            ctx.lineTo(width, height);
        }
        ctx.closePath();
        ctx.fillStyle = '#010a14';
        ctx.fill();

        pipelineRenderSolidRocks(false);
        pipelineRenderWeaponGraveyard(false);

        // Foreground Ridge
        ctx.beginPath();
        if (ridgeLayerFront.length > 0) {
            ctx.moveTo(0, height);
            ctx.lineTo(ridgeLayerFront[0].x, ridgeLayerFront[0].y);
            for (let i = 1; i < ridgeLayerFront.length; i++) {
                ctx.lineTo(ridgeLayerFront[i].x, ridgeLayerFront[i].y);
            }
            ctx.lineTo(width, height);
        }
        ctx.closePath();
        ctx.fillStyle = '#01050a';
        ctx.fill();

        pipelineRenderSolidRocks(true);
        pipelineRenderWeaponGraveyard(true);
        pipelineRenderFallenButtonMesh();

        if (portalTransitionProgress > 0) {
            pipelineRenderEnergyConduits(runningUprockFrameY);
        }

        pipelineRenderViscousMagmaOcean();
        pipelineRenderAshSystem();

        requestAnimationFrame(executeMasterEnginePipelineTick);
    }

    // Drag tracking system parameters
    window.addEventListener('mousedown', function(e) {
        if(e.target.tagName === 'INPUT' || e.target.tagName === 'BUTTON' || e.target.tagName === 'LABEL') return;
        isDragging = true;
        previousMouseX = e.clientX;
    });

    window.addEventListener('mousemove', function(e) {
        userMouse.targetX = e.clientX;
        userMouse.targetY = e.clientY;
        userMouse.trackingActive = true;

        if (isDragging && portalSummoned) {
            let deltaX = e.clientX - previousMouseX;
            targetRotationY += deltaX * 0.35;
            previousMouseX = e.clientX;
        }
    });

    window.addEventListener('mouseup', function() { isDragging = false; });
    window.addEventListener('mouseleave', function() { isDragging = false; userMouse.trackingActive = false; });

    window.addEventListener('resize', function() {
        buildRealmSystemGeometry();
    });

    buildRealmSystemGeometry();
    requestAnimationFrame(executeMasterEnginePipelineTick);

})();