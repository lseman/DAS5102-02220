# mrw_env_enhanced.py — Multi-Robot Warehouse with Concurrent Data Structures
"""
Educational Multi-Robot Warehouse Simulation
=============================================

This file contains:
1. SKELETON concurrent data structures (YOU MUST IMPLEMENT THESE!)
2. The warehouse simulation environment (DO NOT MODIFY)
3. Advanced visualization system (DO NOT MODIFY)

⚠️  IMPORTANT: The data structures have NO implementation - only 'pass'!
    You must write the actual code to make them work.

YOUR TASKS:
-----------
CHALLENGE 1: Implement ConcurrentTaskBoard (lines ~60-150)
    - Thread-safe priority queue for job distribution
    - Must support: pop_best(), push(), __len__(), get_sorted_jobs()
    - No baseline provided - start from scratch!

CHALLENGE 2: Implement ReservationTable (lines ~240-330)
    - Concurrent 3D hash set for space-time reservations
    - Must support: reserve_path(), reserve_single(), advance_time()
    - No baseline provided - design your own approach!

CHALLENGE 3 (ADVANCED): Implement WorkStealingTaskBoard (lines ~150-230)
    - Per-robot deques with stealing protocol
    - Must support: pop_for_robot(), push_for_robot(), __len__(), get_sorted_jobs()
    - Environment automatically detects and uses this!

HOW TO TEST:
------------
1. Implement the classes (in this file or in my_solution.py)
2. Run this file: python mrw_env_enhanced.py
3. Watch the visualization - see your algorithm in action!
4. Check metrics: efficiency %, collisions, wait time

APPROACHES TO TRY:
------------------
For Task Queue:
- Coarse lock (simple but slow under contention)
- Lock striping (multiple heaps, lock per heap)
- Fine-grained locking (lock per node/level)
- Lock-free skip list (advanced - no locks at all!)
- Hierarchical queues (separate high/medium/low priority)

For Reservation Table:
- Coarse lock (simple but doesn't scale)
- Lock striping by spatial region
- Concurrent hash map with fine-grained locks
- Optimistic concurrency with CAS
- Read-write locks (many readers, few writers)

WHAT NOT TO CHANGE:
-------------------
- MRWEnv class (the simulation logic)
- animate_ultra() method (the visualization)
- Robot, Job dataclasses
- The step() method (it auto-detects work-stealing!)

Good luck! Remember: concurrency is hard, but the visualization makes debugging fun! 🤖
"""

from __future__ import annotations

import copy
import random
import threading
from dataclasses import dataclass, field
from typing import Dict, List, Optional, Set, Tuple

import matplotlib.pyplot as plt
import numpy as np
from matplotlib import animation
from matplotlib.lines import Line2D
from matplotlib.patches import Circle, FancyBboxPatch, Rectangle, Wedge

Coord = Tuple[int, int]
TimeCoord = Tuple[int, int, int]
FREE, SHELF, DOCK, WALL = 0, 1, 2, 3

# ============ VISUALIZATION THEMES ============
THEMES = {
    'cyberpunk': {
        'bg': '#0a0e27',
        'grid': '#ff00ff',
        'shelf': '#00ffff',
        'dock': '#ff1493',
        'robot': plt.cm.plasma,
        'trail_alpha': 0.6,
        'name': 'CYBERPUNK MODE'
    },
    'retro': {
        'bg': '#1a1a2e',
        'grid': '#16213e',
        'shelf': '#e94560',
        'dock': '#0f3460',
        'robot': plt.cm.Set3,
        'trail_alpha': 0.5,
        'name': 'RETRO ARCADE'
    },
    'nature': {
        'bg': '#f0f8ea',
        'grid': '#c8e6c9',
        'shelf': '#8d6e63',
        'dock': '#ffb74d',
        'robot': plt.cm.Accent,
        'trail_alpha': 0.4,
        'name': 'NATURE THEME'
    },
    'industrial': {
        'bg': '#263238',
        'grid': '#37474f',
        'shelf': '#ff6f00',
        'dock': '#ffd600',
        'robot': plt.cm.tab10,
        'trail_alpha': 0.5,
        'name': 'INDUSTRIAL'
    }
}

# ============ JOBS & CONCURRENT STRUCTURES ============
@dataclass(order=True)
class Job:
    priority: float
    pick: Coord = field(compare=False)
    drop: Coord = field(compare=False)
    id: int = field(compare=False, default=-1)
    deadline: Optional[int] = field(compare=False, default=None)
    assigned_time: Optional[int] = field(compare=False, default=None)
    completion_time: Optional[int] = field(compare=False, default=None)


# ============================================================================
# CHALLENGE 1: CONCURRENT TASK QUEUE
# ============================================================================
# TODO: Implement your thread-safe priority queue here!
# 
# Requirements:
# - Multiple robots will call pop_best() concurrently
# - Must be thread-safe (no race conditions!)
# - Lower priority value = higher urgency (min-heap)
# - Optimize for high contention scenarios
#
# Implementation ideas:
# - Fine-grained locking (lock per node/level)
# - Lock-free using atomic operations (CAS)
# - Hierarchical queues (separate high/medium/low priority)
# - Or use the baseline implementation below to get started
# ============================================================================

class ConcurrentTaskBoard:
    """
    STUDENT IMPLEMENTATION: Thread-safe priority queue for job distribution.
    
    This is a BASELINE implementation using coarse-grained locking.
    Your job: Make it faster! Try:
    - Lock striping
    - Lock-free algorithms
    - Fine-grained locking
    - Hierarchical priority bands
    """
    
    def __init__(self, jobs: List[Job]):
        """
        Initialize your concurrent queue with initial jobs.
        
        Args:
            jobs: List of Job objects to initialize the queue
        """
        # BASELINE IMPLEMENTATION - You can improve this!
        import heapq
        self._heapq = heapq
        self._lock = threading.Lock()
        self._heap = jobs[:]
        self._heapq.heapify(self._heap)
        
        # TODO: Replace with your implementation
        # Ideas:
        # - Use multiple heaps with lock striping
        # - Implement lock-free skip list
        # - Create priority bands (high/medium/low)
        pass

    def pop_best(self) -> Optional[Job]:
        """
        Remove and return job with lowest priority (most urgent).
        Called concurrently by multiple robots!
        
        Returns:
            Job with lowest priority value, or None if empty
        """
        # BASELINE IMPLEMENTATION
        with self._lock:
            if not self._heap:
                return None
            return self._heapq.heappop(self._heap)
        
        # TODO: Implement your lock-free or fine-grained version
        pass

    def push(self, job: Job) -> None:
        """
        Add a job to the queue.
        Must be thread-safe!
        
        Args:
            job: Job to add to queue
        """
        # BASELINE IMPLEMENTATION
        with self._lock:
            self._heapq.heappush(self._heap, job)
        
        # TODO: Implement your optimized version
        pass
    
    def __len__(self) -> int:
        """Return number of jobs in queue (thread-safe)"""
        # BASELINE IMPLEMENTATION
        with self._lock:
            return len(self._heap)
        
        # TODO: Implement your version
        pass


# ============================================================================
# CHALLENGE 3: WORK-STEALING TASK SCHEDULER (ADVANCED)
# ============================================================================
# TODO: Implement work-stealing for better load balancing!
#
# Concept:
# - Each robot has its own deque
# - Robots take work from front of own deque (FIFO)
# - Idle robots "steal" from back of other robots' deques
# - Must handle race conditions during stealing!
#
# GOOD NEWS: The simulation automatically detects work-stealing!
# Just implement pop_for_robot() instead of pop_best() and it works!
#
# This is OPTIONAL but gives best performance under variable load
# ============================================================================

class WorkStealingTaskBoard:
    """
    CHALLENGE 3: Work-stealing scheduler with per-robot deques.
    
    Advanced concurrent data structure combining:
    - Per-robot double-ended queues
    - Steal protocol (random victim selection)
    - Fine-grained synchronization
    
    NOTE: The environment will automatically detect and use this!
    It checks for pop_for_robot() method and uses it if available.
    """
    
    def __init__(self, jobs: List[Job], num_robots: int):
        """
        Initialize work-stealing scheduler.
        
        Args:
            jobs: Initial jobs to distribute across robot deques
            num_robots: Number of robots (one deque per robot)
        """
        # TODO: Create one deque per robot
        # TODO: Distribute jobs across deques (round-robin or random)
        # TODO: Add locks per deque (or use lock-free deques)
        pass
    
    def pop_for_robot(self, robot_id: int) -> Optional[Job]:
        """
        Get work for a specific robot.
        
        Strategy:
        1. Try to pop from own deque (front - FIFO)
        2. If empty, attempt to steal from random victim (back - LIFO)
        3. Handle race conditions during stealing
        
        Args:
            robot_id: ID of robot requesting work
            
        Returns:
            Job if found, None if all deques empty
        """
        # TODO: Implement work-stealing logic
        # 1. Try own deque first
        # 2. If empty, randomly pick victim robot
        # 3. Try to steal from victim's back
        # 4. Handle contention (multiple stealers)
        pass
    
    def push_for_robot(self, robot_id: int, job: Job) -> None:
        """
        Add job to specific robot's deque.
        
        Args:
            robot_id: Target robot
            job: Job to add
        """
        # TODO: Add to robot's deque (typically to back)
        pass
    
    def __len__(self) -> int:
        """Total number of jobs across all deques"""
        # TODO: Sum lengths of all deques
        pass
    
    def get_sorted_jobs(self) -> List[Job]:
        """Collect all jobs from all deques and sort for visualization"""
        # TODO: Gather jobs from all deques
        # TODO: Sort by priority
        pass


# ============================================================================
# CHALLENGE 2: SPATIAL RESERVATION TABLE  
# ============================================================================
# TODO: Implement concurrent 3D hash set for space-time reservations!
#
# Requirements:
# - Store (x, y, t) tuples representing "cell occupied at time t"
# - Support atomic batch operations (reserve entire path or nothing)
# - Efficient cleanup of old reservations
# - Thread-safe for concurrent reserve/check operations
#
# Implementation ideas:
# - Lock striping by spatial region
# - Concurrent hash map with fine-grained locks
# - Optimistic concurrency (CAS-based)
# - Lock ordering to prevent deadlocks
# ============================================================================

class ReservationTable:
    """
    STUDENT IMPLEMENTATION: Concurrent 3D spatial hash set.
    
    NO BASELINE PROVIDED - You must implement this from scratch!
    
    Requirements:
    - Store (x, y, t) tuples representing occupied space-time cells
    - Thread-safe operations for concurrent reservations
    - Atomic batch operations (reserve entire path or nothing)
    - Efficient cleanup of old reservations
    
    Consider:
    - What data structure? (hash set, spatial grid, concurrent map?)
    - How to synchronize? (global lock, striping, lock-free?)
    - How to make batch operations atomic?
    """
    
    def __init__(self):
        """
        Initialize your reservation data structure.
        
        Must track (x, y, t) tuples for space-time reservations.
        
        TODO: Initialize your data structure
        Examples:
        - Simple: self._occ = set(); self._lock = Lock()
        - Striped: self._regions = [{} for _ in range(N)]
        - Concurrent map: self._map = ConcurrentHashMap()
        - Spatial: self._grid = [[{} for _ in range(W)] for _ in range(H)]
        """
        # TODO: Initialize your reservation structure
        pass

    def advance_time(self, t_cur: int) -> None:
        """
        Clean up reservations before current time.
        Called once per simulation tick.
        
        Args:
            t_cur: Current time - remove all reservations with t < t_cur
            
        TODO: Implement efficient cleanup
        Consider:
        - How do you iterate over reservations?
        - Should you lock during entire cleanup?
        - Can you do lazy deletion?
        - What about batch cleanup?
        """
        # TODO: Implement your cleanup logic
        pass

    def reserve_path(self, path: List[Coord], t0: int) -> bool:
        """
        Atomically reserve entire path or nothing (all-or-nothing).
        
        This is like a database transaction!
        - path[0] reserves at time t0
        - path[1] reserves at time t0+1
        - path[i] reserves at time t0+i
        
        CRITICAL: Must be ATOMIC - either ALL cells reserved or NONE!
        
        Args:
            path: List of (x,y) coordinates
            t0: Starting time
            
        Returns:
            True if all reserved successfully, False if any conflict
            
        TODO: Implement atomic batch reservation
        Consider:
        - Two-phase: check all, then reserve all
        - What if another robot checks between your check and reserve?
        - How do you ensure atomicity?
        - Lock ordering to prevent deadlock?
        """
        # TODO: Implement your atomic path reservation
        pass

    def reserve_single(self, cell: Coord, t: int) -> bool:
        """
        Reserve a single cell at given time.
        
        Args:
            cell: (x, y) coordinate
            t: Time to reserve
            
        Returns:
            True if reserved, False if already taken
            
        TODO: Implement single-cell reservation
        Consider:
        - How do you check if (x, y, t) is free?
        - How do you atomically claim it?
        - What synchronization is needed?
        """
        # TODO: Implement your single-cell reservation
        pass

    def get_sorted_jobs(self) -> List[Job]:
        """
        Return sorted copy of all jobs for visualization.
        Does not modify internal state.
        
        Returns:
            List of jobs sorted by priority
        """
        # BASELINE IMPLEMENTATION
        with self._lock:
            return sorted(copy.copy(self._heap), key=lambda j: j.priority)
        
        # TODO: Implement your version
        pass

# ============ ROBOTS & ENVIRONMENT ============
@dataclass
class Robot:
    id: int
    pos: Coord
    carrying: bool = False
    job: Optional[Job] = None
    path: List[Coord] = field(default_factory=list)
    color_idx: int = 0
    explode_time: Optional[int] = None
    jobs_completed: int = 0
    total_distance: float = 0.0
    wait_time: int = 0


class MRWEnv:
    def __init__(self, W=20, H=14, num_robots=5, num_jobs=12, seed=7, debug: bool = False):
        random.seed(seed)
        np.random.seed(seed)
        self.W, self.H = W, H
        self.t = 0
        self.debug = debug
        self._logs: List[str] = []
        
        # Performance metrics
        self.total_jobs_completed = 0
        self.collision_count = 0
        self.total_wait_time = 0
        self.job_completion_times: List[int] = []
        
        # Grid setup
        self.grid = np.zeros((H, W), dtype=np.int32)
        for i in range(H):
            self.grid[i, 0] = WALL
            self.grid[i, W-1] = WALL
        for j in range(W):
            self.grid[0, j] = WALL
            self.grid[H-1, j] = WALL
        
        # Shelves & Docks
        for _ in range(max(10, W * H // 12)):
            y, x = np.random.randint(1, H - 1), np.random.randint(1, W - 1)
            if self.grid[y, x] == FREE:
                self.grid[y, x] = SHELF
        for _ in range(max(3, W // 6)):
            y, x = np.random.randint(1, H - 1), np.random.randint(1, W - 1)
            if self.grid[y, x] == FREE:
                self.grid[y, x] = DOCK
        
        # Robots
        empties = list(zip(*np.where(self.grid == FREE)))
        np.random.shuffle(empties)
        self.robots: List[Robot] = []
        for rid in range(num_robots):
            if empties:
                y, x = empties.pop()
            else:
                y, x = np.random.randint(1, H-1), np.random.randint(1, W-1)
            self.grid[y, x] = FREE
            self.robots.append(Robot(rid, (x, y), color_idx=rid % 10))
        
        # Jobs
        shelves = list(zip(*np.where(self.grid == SHELF)))
        docks = list(zip(*np.where(self.grid == DOCK)))
        jobs: List[Job] = []
        for jid in range(num_jobs):
            sy, sx = random.choice(shelves)
            dy, dx = random.choice(docks)
            dist = abs(dx - sx) + abs(dy - sy)
            prio = dist + 3.0 * (jid % 3)
            jobs.append(Job(prio, (sx, sy), (dx, dy), id=jid))
        
        self.taskboard = ConcurrentTaskBoard(jobs)
        self.reservations = ReservationTable()
        self.trajectories: Dict[int, List[Coord]] = {r.id: [r.pos] for r in self.robots}
        self.heatmap = np.zeros((H, W), dtype=np.float32)

    def log(self, s: str) -> None:
        if self.debug:
            self._logs.append(s)

    def shortest_path_greedy(self, src: Coord, tgt: Coord, max_len: int = 256) -> List[Coord]:
        path = [src]
        x, y = src
        tx, ty = tgt
        steps = 0
        while (x, y) != (tx, ty) and steps < max_len:
            if x < tx: x += 1
            elif x > tx: x -= 1
            elif y < ty: y += 1
            elif y > ty: y -= 1
            path.append((x, y))
            steps += 1
        return path

    def done(self) -> bool:
        return all(r.job is None for r in self.robots) and len(self.taskboard) == 0

    def step(self) -> None:
        """
        Single simulation tick - DO NOT MODIFY (unless doing Challenge 3).
        
        This method shows how your concurrent data structures are used:
        1. Robots call taskboard.pop_best() to claim jobs (CONCURRENT!)
        2. Robots call reservations.reserve_path() to avoid collisions (CONCURRENT!)
        
        Study this to understand the concurrency patterns!
        """
        self.t += 1
        self.reservations.advance_time(self.t)
        
        # Update heatmap
        for r in self.robots:
            x, y = r.pos
            if 0 <= y < self.H and 0 <= x < self.W:
                self.heatmap[y, x] += 1
        
        # Claim jobs - THIS IS WHERE CONCURRENCY HAPPENS!
        # Multiple robots compete for jobs by calling pop_best()
        # OR pop_for_robot() if using work-stealing (Challenge 3)
        for r in self.robots:
            if r.job is None:
                # Check if using work-stealing interface
                if hasattr(self.taskboard, 'pop_for_robot'):
                    # Challenge 3: Work-stealing scheduler
                    r.job = self.taskboard.pop_for_robot(r.id)  # <-- WORK-STEALING!
                else:
                    # Challenge 1: Standard concurrent queue
                    r.job = self.taskboard.pop_best()  # <-- YOUR CONCURRENT QUEUE!
                
                if r.job is not None:
                    r.job.assigned_time = self.t
                    self.log(f"[r{r.id}] claimed job {r.job.id}")
        
        # Plan and move
        for r in self.robots:
            if r.job is None:
                self.trajectories[r.id].append(r.pos)
                continue
            
            target = r.job.drop if r.carrying else r.job.pick
            need_replan = (len(r.path) <= 1) or (r.path[-1] != target) or (r.path[0] != r.pos)
            
            if need_replan:
                r.path = self.shortest_path_greedy(r.pos, target)
            
            if len(r.path) <= 1:
                if not r.carrying and r.pos == r.job.pick:
                    r.carrying = True
                elif r.carrying and r.pos == r.job.drop:
                    r.carrying = False
                    r.job.completion_time = self.t
                    r.jobs_completed += 1
                    self.total_jobs_completed += 1
                    
                    # Calculate job duration
                    if r.job.assigned_time:
                        duration = self.t - r.job.assigned_time
                        self.job_completion_times.append(duration)
                    
                    r.explode_time = self.t
                    r.job = None
                self.trajectories[r.id].append(r.pos)
                continue
            
            next_cell = r.path[1]
            k = min(5, len(r.path) - 1)
            future_segment = r.path[1:1 + k]
            
            # Try to reserve path - CONCURRENT SPATIAL COORDINATION!
            ok_future = self.reservations.reserve_path(future_segment, self.t + 1)  # <-- YOUR RESERVATION TABLE!
            
            moved = False
            if ok_future:
                old_pos = r.pos
                r.pos = next_cell
                r.path = r.path[1:]
                r.total_distance += abs(next_cell[0] - old_pos[0]) + abs(next_cell[1] - old_pos[1])
                moved = True
            else:
                # Fallback: try single-cell reservation
                ok_now = self.reservations.reserve_single(next_cell, self.t)  # <-- ANOTHER CONCURRENT CALL!
                if ok_now:
                    old_pos = r.pos
                    r.pos = next_cell
                    r.path = r.path[1:]
                    r.total_distance += abs(next_cell[0] - old_pos[0]) + abs(next_cell[1] - old_pos[1])
                    moved = True
                else:
                    r.path = [r.pos] + self.shortest_path_greedy(r.pos, target)
                    r.wait_time += 1
                    self.total_wait_time += 1
                    self.collision_count += 1
            
            if not r.carrying and r.pos == r.job.pick:
                r.carrying = True
            if r.carrying and r.pos == r.job.drop:
                r.carrying = False
                r.job.completion_time = self.t
                r.jobs_completed += 1
                self.total_jobs_completed += 1
                
                if r.job.assigned_time:
                    duration = self.t - r.job.assigned_time
                    self.job_completion_times.append(duration)
                
                r.explode_time = self.t
                r.job = None
            
            self.trajectories[r.id].append(r.pos)

    def get_performance_stats(self) -> Dict:
        """Calculate performance metrics"""
        avg_completion = np.mean(self.job_completion_times) if self.job_completion_times else 0
        efficiency = (self.total_jobs_completed / max(1, self.t)) * 100
        avg_distance = np.mean([r.total_distance for r in self.robots])
        
        return {
            'jobs_done': self.total_jobs_completed,
            'avg_time': avg_completion,
            'efficiency': efficiency,
            'collisions': self.collision_count,
            'avg_distance': avg_distance,
            'total_wait': self.total_wait_time
        }

    def animate_ultra(self, max_steps=500, interval_ms=50, save_path: Optional[str] = None, 
                     dpi=120, theme='cyberpunk', show_heatmap=False):
        """
        ULTRA ENHANCED visualization with:
        - Multiple themes
        - Performance dashboard
        - Achievement popups
        - Particle effects
        - Activity heatmap overlay
        - Progress bars
        - Celebration effects
        """
        theme_config = THEMES.get(theme, THEMES['cyberpunk'])
        colors = theme_config['robot'](np.linspace(0, 1, 10))
        
        # Create figure with dashboard
        fig = plt.figure(figsize=(16, 9))
        fig.patch.set_facecolor(theme_config['bg'])
        
        # Main warehouse view
        ax_main = plt.subplot2grid((3, 4), (0, 0), colspan=3, rowspan=3)
        
        # Dashboard panels
        ax_stats = plt.subplot2grid((3, 4), (0, 3))
        ax_queue = plt.subplot2grid((3, 4), (1, 3))
        ax_progress = plt.subplot2grid((3, 4), (2, 3))
        
        # Style main plot
        ax_main.set_xlim(-0.5, self.W - 0.5)
        ax_main.set_ylim(-0.5, self.H - 0.5)
        ax_main.set_aspect("equal")
        ax_main.set_facecolor(theme_config['bg'])
        ax_main.grid(True, alpha=0.2, color=theme_config['grid'], linewidth=0.5)
        ax_main.set_title(theme_config['name'], fontsize=16, fontweight='bold', 
                         color='white', pad=10)
        
        # Heatmap overlay
        heatmap_img = None
        if show_heatmap:
            heatmap_img = ax_main.imshow(self.heatmap, cmap='hot', alpha=0.3, 
                                        extent=[-0.5, self.W-0.5, -0.5, self.H-0.5],
                                        origin='lower', interpolation='gaussian')
        
        # Static elements
        shelf_y, shelf_x = np.where(self.grid == SHELF)
        dock_y, dock_x = np.where(self.grid == DOCK)
        ax_main.scatter(shelf_x, shelf_y, marker="s", s=150, 
                       color=theme_config['shelf'], edgecolors='white', 
                       linewidth=2, alpha=0.8, label='Shelves')
        ax_main.scatter(dock_x, dock_y, marker="D", s=180, 
                       color=theme_config['dock'], edgecolors='white', 
                       linewidth=2, alpha=0.9, label='Docks')
        
        # Robots
        robot_positions = np.array([[float(r.pos[0]), float(r.pos[1])] for r in self.robots])
        robot_colors = [colors[r.color_idx] for r in self.robots]
        robot_sc = ax_main.scatter(robot_positions[:, 0], robot_positions[:, 1], 
                                  s=200, c=robot_colors, marker="o", 
                                  edgecolors='white', linewidth=2, zorder=10)
        
        # Robot labels with fancy boxes
        robot_labels = []
        for i, r in enumerate(self.robots):
            label = ax_main.annotate(f'R{i}', (r.pos[0], r.pos[1]), 
                                    xytext=(0, 15), textcoords='offset points',
                                    fontsize=10, fontweight='bold', ha='center', 
                                    color='white',
                                    bbox=dict(boxstyle='round,pad=0.4', 
                                            facecolor=colors[r.color_idx], 
                                            alpha=0.9, edgecolor='white', linewidth=2))
            robot_labels.append(label)
        
        # Trails
        trail_lines = {}
        for r in self.robots:
            line, = ax_main.plot([float(r.pos[0])], [float(r.pos[1])], 
                                linewidth=3, alpha=theme_config['trail_alpha'], 
                                color=colors[r.color_idx], linestyle='--')
            trail_lines[r.id] = line
        
        # Explosion effects
        explosions: List[Tuple[Coord, int, List]] = []
        
        # Achievement popup
        achievement_text = ax_main.text(self.W/2, self.H-1, "", fontsize=14, 
                                       fontweight='bold', ha='center', va='top',
                                       color='#FFD700', alpha=0,
                                       bbox=dict(boxstyle='round,pad=0.8', 
                                               facecolor='#1a1a1a', alpha=0.9,
                                               edgecolor='#FFD700', linewidth=3))
        achievement_alpha = 0
        achievement_counter = 0
        
        # Dashboard styling
        for ax in [ax_stats, ax_queue, ax_progress]:
            ax.set_facecolor('#1a1a1a')
            ax.axis('off')
        
        # Stats display
        stats_text = ax_stats.text(0.05, 0.95, "", va='top', fontsize=9, 
                                  color='white', family='monospace',
                                  bbox=dict(boxstyle='round,pad=0.5', 
                                          facecolor='#2a2a3a', alpha=0.9))
        ax_stats.set_title('PERFORMANCE', fontsize=10, color='#00ff00', 
                          fontweight='bold', pad=5)
        
        # Queue display
        queue_text = ax_queue.text(0.05, 0.95, "", va='top', fontsize=8, 
                                  color='white', family='monospace',
                                  bbox=dict(boxstyle='round,pad=0.5', 
                                          facecolor='#2a2a3a', alpha=0.9))
        ax_queue.set_title('TASK QUEUE', fontsize=10, color='#ff00ff', 
                          fontweight='bold', pad=5)
        
        # Progress bars
        progress_text = ax_progress.text(0.05, 0.95, "", va='top', fontsize=8, 
                                        color='white', family='monospace',
                                        bbox=dict(boxstyle='round,pad=0.5', 
                                                facecolor='#2a2a3a', alpha=0.9))
        ax_progress.set_title('PROGRESS', fontsize=10, color='#00ffff', 
                            fontweight='bold', pad=5)
        
        ax_main.legend(loc='upper left', fontsize=9, facecolor='#1a1a1a', 
                      edgecolor='white', labelcolor='white')
        
        # Milestone tracking
        milestones = [3, 5, 10, len(self.taskboard.get_sorted_jobs())]
        milestone_idx = 0
        
        def init():
            return [robot_sc] + robot_labels + list(trail_lines.values()) + \
                   [stats_text, queue_text, progress_text, achievement_text]
        
        def update(frame_idx):
            nonlocal achievement_alpha, achievement_counter, milestone_idx
            
            if not self.done() and frame_idx < max_steps:
                self.step()
            
            # Update robot positions
            pos = np.array([[float(r.pos[0]), float(r.pos[1])] for r in self.robots])
            robot_sc.set_offsets(pos)
            sizes = [250 if r.carrying else 200 for r in self.robots]
            robot_sc.set_sizes(sizes)
            
            # Update labels
            for i, r in enumerate(self.robots):
                label_text = f'R{i}*' if r.carrying else f'R{i}'
                robot_labels[i].set_text(label_text)
                robot_labels[i].xy = (r.pos[0], r.pos[1])
            
            # Update trails
            for r in self.robots:
                xs = [float(p[0]) for p in self.trajectories[r.id][-30:]]  # Last 30 points
                ys = [float(p[1]) for p in self.trajectories[r.id][-30:]]
                trail_lines[r.id].set_data(xs, ys)
            
            # Update heatmap
            if show_heatmap and heatmap_img:
                heatmap_img.set_data(self.heatmap)
            
            # Explosions - create firework-like particles
            for r in self.robots:
                if r.explode_time == self.t:
                    particles = []
                    for _ in range(12):  # 12 particles
                        angle = random.uniform(0, 2 * np.pi)
                        circle = Circle((r.pos[0], r.pos[1]), 0.1, 
                                      color=colors[r.color_idx], alpha=0.8)
                        ax_main.add_patch(circle)
                        particles.append((circle, angle))
                    explosions.append((r.pos, self.t, particles))
                    r.explode_time = None
            
            # Update explosions
            to_remove = []
            for i, (center, start_t, particles) in enumerate(explosions):
                age = self.t - start_t
                if age > 15:
                    to_remove.append(i)
                else:
                    for circle, angle in particles:
                        speed = 0.15
                        offset_x = speed * age * np.cos(angle)
                        offset_y = speed * age * np.sin(angle)
                        circle.center = (center[0] + offset_x, center[1] + offset_y)
                        alpha = max(0, 1 - age / 15)
                        circle.set_alpha(alpha)
                        radius = 0.1 + age * 0.05
                        circle.set_radius(radius)
            
            for idx in sorted(to_remove, reverse=True):
                for circle, _ in explosions[idx][2]:
                    circle.remove()
                del explosions[idx]
            
            # Update stats
            stats = self.get_performance_stats()
            stats_str = f"""TIME: {self.t}
COMPLETED: {stats['jobs_done']}
EFFICIENCY: {stats['efficiency']:.1f}%
COLLISIONS: {stats['collisions']}
AVG TIME: {stats['avg_time']:.1f}
TOTAL WAIT: {stats['total_wait']}"""
            stats_text.set_text(stats_str)
            
            # Update queue
            jobs = self.taskboard.get_sorted_jobs()[:8]  # Top 8
            if jobs:
                queue_str = '\n'.join([f'#{j.id} (p:{j.priority:.0f})' for j in jobs])
                if len(self.taskboard.get_sorted_jobs()) > 8:
                    queue_str += f'\n... +{len(self.taskboard.get_sorted_jobs())-8} more'
            else:
                queue_str = 'ALL DONE!'
            queue_text.set_text(queue_str)
            
            # Update progress
            active_robots = sum(1 for r in self.robots if r.job is not None)
            progress_str = f"""ACTIVE: {active_robots}/{len(self.robots)}
IDLE: {len(self.robots) - active_robots}

ROBOT STATS:"""
            for r in self.robots[:5]:  # Top 5
                progress_str += f'\nR{r.id}: {r.jobs_completed} done'
            progress_text.set_text(progress_str)
            
            # Achievement system
            if milestone_idx < len(milestones) and stats['jobs_done'] >= milestones[milestone_idx]:
                achievement_messages = [
                    "FIRST DELIVERIES!",
                    "ON FIRE!",
                    "AMAZING WORK!",
                    "ALL JOBS COMPLETE!"
                ]
                achievement_text.set_text(achievement_messages[milestone_idx])
                achievement_alpha = 1.0
                achievement_counter = 30  # Show for 30 frames
                milestone_idx += 1
            
            # Fade achievement
            if achievement_counter > 0:
                achievement_counter -= 1
                achievement_alpha = achievement_counter / 30
                achievement_text.set_alpha(achievement_alpha)
                achievement_text.get_bbox_patch().set_alpha(achievement_alpha * 0.9)
            
            return [robot_sc] + robot_labels + list(trail_lines.values()) + \
                   [stats_text, queue_text, progress_text, achievement_text] + \
                   [p[0] for exp in explosions for p in exp[2]]
        
        ani = animation.FuncAnimation(
            fig, update, init_func=init,
            frames=max_steps, interval=interval_ms, blit=False, repeat=False
        )
        
        plt.tight_layout()
        
        if save_path:
            fps = max(1, 1000 // interval_ms)
            ext = save_path.lower().rsplit(".", 1)[-1] if "." in save_path else ""
            if ext in {"mp4", "mkv", "mov", "webm"}:
                Writer = animation.FFMpegWriter
                writer = Writer(fps=fps, metadata={"artist": "MRW Ultra"}, bitrate=2400)
                ani.save(save_path, writer=writer, dpi=dpi)
            elif ext == "gif":
                from matplotlib.animation import PillowWriter
                writer = PillowWriter(fps=fps)
                ani.save(save_path, writer=writer, dpi=dpi)
            plt.close(fig)
        else:
            plt.show()
        
        return ani


# ============ EXAMPLE USAGE ============
if __name__ == "__main__":
    # Create environment
    env = MRWEnv(W=25, H=18, num_robots=6, num_jobs=15, seed=42)
    
    # Try different themes:
    # 'cyberpunk', 'retro', 'nature', 'industrial'
    
    # Animate with ultra visualization
    env.animate_ultra(
        max_steps=400,
        interval_ms=50,
        theme='cyberpunk',  # Change theme here!
        show_heatmap=True,  # Enable activity heatmap
        # save_path='warehouse_ultra.mp4'  # Uncomment to save
    )
    
    # Print final stats
    print("\n" + "="*50)
    print("FINAL PERFORMANCE REPORT")
    print("="*50)
    stats = env.get_performance_stats()
    for key, value in stats.items():
        print(f"{key}: {value}")
