import os
import seaborn as sns
import pandas as pd
import matplotlib.pyplot as plt
import subprocess

def get_file_names(directory):
    return [f for f in os.listdir(directory) if os.path.isfile(os.path.join(directory, f))]

file_names = get_file_names('./data')
progress = {"Arshia" : -100, "Jinu" : 0, "Hasti" : 0, "MohammadReza" : 0, "Blake" : 0, "Mahsa" : 0,"Hasib" : 0, "Aishneet" : 0, "Peyton" : 0, "Dr. Zand": 0, "Nina" : 0}

for item in file_names:
    for key, value in progress.items():
        if (item.startswith(key)):
            progress[key] = value + 1


# Assuming 'progress' is your dictionary
df = pd.DataFrame(progress.items(), columns=['Name', 'Trials'])

# Find the winner (max trials)
winner = df.loc[df['Trials'].idxmax()]

# Create the figure and axis objects
fig, ax = plt.subplots(figsize=(14, 8))

# Set a dark background
ax.set_facecolor('#2F2F2F')
fig.patch.set_facecolor('#2F2F2F')

# Create the bar plot
sns.barplot(data=df, x='Name', y='Trials', ax=ax, palette='coolwarm')

# Highlight the winner's bar
ax.patches[df['Trials'].idxmax()].set_facecolor('#FFD700')  # Gold color for the winner

# Customize the plot
plt.xlabel('Participant', fontsize=16, fontweight='bold', color='white')
plt.ylabel('Number of Trials', fontsize=16, fontweight='bold', color='white')

# Improve tick labels
plt.xticks(fontsize=12, color='white', rotation=45, ha='right')
plt.yticks(fontsize=12, color='white')

# Add grid for better readability
plt.grid(True, axis='y', linestyle='--', alpha=0.3, color='gray')

# Remove spines
for spine in ax.spines.values():
    spine.set_visible(False)

# Add value labels on top of each bar
for i, v in enumerate(df['Trials']):
    ax.text(i, v, str(v), ha='center', va='bottom', fontweight='bold', color='white', fontsize=12)

# Highlight the winner with an annotation
ax.annotate(f'Leader: {winner["Name"]}\nTrials: {winner["Trials"]}',
            xy=(df['Trials'].idxmax(), winner['Trials']),
            xytext=(0, 30), textcoords='offset points',
            fontsize=14, fontweight='bold', color='#FFD700',
            ha='center', va='bottom',
            bbox=dict(boxstyle='round,pad=0.5', fc='#4A4A4A', ec='none', alpha=0.6),
            arrowprops=dict(arrowstyle='->', connectionstyle='arc3,rad=0', color='#FFD700'))


# Add a text on the top right of the graph
plt.text(0.95, 0.95, 'Collect data to win a Prize!', ha='right', va='top', transform=ax.transAxes, fontsize=14, fontweight='bold', color='white')


# Adjust layout and display the plot
plt.tight_layout()
# plt.show()


# Save the plot as plot.img in the current directory
plt.savefig('./plot.jpeg')


# Get the absolute path of the current working directory
current_dir = os.path.abspath(os.getcwd())
wallpaper_path = os.path.join(current_dir, 'plot.jpeg')

# Update the wallpaper using the absolute path
subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri-dark", f"file://{wallpaper_path}"])
subprocess.run(["gsettings", "set", "org.gnome.desktop.background", "picture-uri", f"file://{wallpaper_path}"])

